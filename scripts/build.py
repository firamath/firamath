'''Build FiraMath.glyphspackage.
'''

import copy
import os
import sys
import time

from fontmake.font_project import FontProject
from fontmake.instantiator import Instantiator

import fontTools
from fontTools.ttLib import TTFont
from fontTools.designspaceLib import DesignSpaceDocument

import glyphsLib
from glyphsLib import GSComponent, GSFont, GSGlyph, GSLayer, GSNode, GSPath
from glyphsLib.parser import Parser

from math_table import math_table

def read_glyphs_package(path: str) -> GSFont:
    with open(os.path.join(path, 'fontinfo.plist'), 'r') as fontinfo_plist:
        fontinfo = fontinfo_plist.read()
    with open(os.path.join(path, 'order.plist'), 'r') as order_plist:
        order: list[str] = Parser().parse(order_plist.read())
    insert_pos = fontinfo.find('instances = (')
    glyphs = 'glyphs = (\n' + ',\n'.join(read_glyph(path, name) for name in order) + '\n);\n'
    return Parser(current_type=GSFont).parse(
        fontinfo[:insert_pos] + glyphs + fontinfo[insert_pos:-1])

def read_glyph(path: str, name: str):
    file_name = glyph_name_to_file_name(name)
    with open(os.path.join(path, 'glyphs', file_name), 'r') as f:
        return f.read()[:-1]

def glyph_name_to_file_name(name: str):
    if name == '.notdef':
        return '_notdef.glyph'
    return ''.join([c + '_' if c.isupper() else c for c in name]) + '.glyph'

def fix_export(font: GSFont):
    '''Change `glyph.export = 0` into `glyph.export = False`.'''
    for glyph in (g for g in font.glyphs if g.export == 0):
        glyph.export = False

def decompose_smart_comp(font: GSFont):
    for glyph in (g for g in font.glyphs if g.category == 'Smart Glyph'):
        decompose_smart_comp_helper_a(glyph)
    for glyph in (g for g in font.glyphs if g.category != 'Smart Glyph'):
        decompose_smart_comp_helper_b(glyph)

def decompose_smart_comp_helper_a(glyph: GSGlyph):
    '''Decompose smart components in `glyph`, where `glyph` is a smart component itself.
    The result layer should contain NO componets.
    '''
    for layer in glyph.layers:
        master_id: str = layer.associatedMasterId
        to_be_removed = []
        for comp in layer.components:
            value_dict = comp.smartComponentValues
            ref_glyph: GSGlyph = comp.component
            to_be_removed.append(comp)
            if 'Group' in value_dict:
                # Normal components
                paths = decompose(comp)
            else:
                # Smart components
                paths = get_smart_comp_path(master_id, ref_glyph, value_dict)
            layer.paths.extend(paths)
        layer._shapes = [s for s in layer._shapes if s not in to_be_removed]

def decompose_smart_comp_helper_b(glyph: GSGlyph):
    '''Decompose smart components in a normal `glyph`.'''
    for layer in glyph.layers:
        master_id: str = layer.associatedMasterId
        to_be_removed = []
        for comp in layer.components:
            if value_dict := comp.smartComponentValues:
                ref_glyph: GSGlyph = comp.component
                to_be_removed.append(comp)
                paths = get_smart_comp_path(master_id, ref_glyph, value_dict)
                layer.paths.extend(paths)
        layer._shapes = [s for s in layer._shapes if s not in to_be_removed]

def decompose(comp: GSComponent) -> list[GSPath]:
    '''Decompose a normal component `comp`.'''
    ref_glyph: GSGlyph = comp.component
    paths = next(
        layer.paths for layer in ref_glyph.layers
        if layer.layerId == comp.parent.associatedMasterId
    )
    result = []
    for path in paths:
        # Manually deepcopy (`copy.deepcopy()`` is very slow here).
        new_path = copy.copy(path)
        new_path.nodes = [GSNode(n.position, type=n.type, smooth=n.smooth) for n in path.nodes]
        new_path.applyTransform(comp.transform)
        result.append(new_path)
    return result

def get_smart_comp_path(master_id: str, glyph: GSGlyph, value_dict: dict) -> list[GSPath]:
    '''Get the path from smart component `glyph` in the master with `master_id`,
    by interpolating between two layers. The axis value is determined via `value_dict`.
    Note that we only support single smart component axis at here.
    '''
    if len(value_dict) == 0:
        interpolation_value = 0
        is_part_n = lambda layer, n: \
            layer.associatedMasterId == master_id and \
            layer.partSelection[next(iter(layer.partSelection.keys()))] == n
    elif len(value_dict) == 1:
        key, value = next(iter(value_dict.items()))
        interpolation_value = next(
            rescale(value, axis.bottomValue, axis.topValue)
            for axis in glyph.smartComponentAxes if axis.name == key
        )
        is_part_n = lambda layer, n: \
            layer.associatedMasterId == master_id and layer.partSelection[key] == n
    else:
        raise ValueError('We only support single smart component axis!')
    layer_0: GSLayer = next(layer for layer in glyph.layers if is_part_n(layer, 1))
    layer_1: GSLayer = next(layer for layer in glyph.layers if is_part_n(layer, 2))
    return [
        interpolate_path(path_0, path_1, interpolation_value)
        for path_0, path_1 in zip(layer_0.paths, layer_1.paths)
    ]

def rescale(x, min, max):
    '''Give `x` rescaled to run from 0 to 1 over the range `min` to `max`.'''
    return (x - min) / (max - min)

def interpolate_path(path_0: GSPath, path_1: GSPath, value) -> GSPath:
    new_path = copy.copy(path_0)
    new_path.nodes = []
    for node_0, node_1 in zip(path_0.nodes, path_1.nodes):
        new_path.nodes.append(interpolate_node(node_0, node_1, value))
    return new_path

def interpolate_node(node_0: GSNode, node_1: GSNode, value) -> GSNode:
    position = (
        round(node_0.position.x * (1 - value) + node_1.position.x * value),
        round(node_0.position.y * (1 - value) + node_1.position.y * value),
    )
    return GSNode(position, type=node_0.type, smooth=node_0.smooth)

def to_ufos(font: GSFont, interpolate: bool = False, default_index: int = 0) -> list:
    ufos, instance_data = glyphsLib.to_ufos(font, include_instances=True)
    if not interpolate:
        return ufos
    designspace: DesignSpaceDocument = instance_data['designspace']
    designspace.default = designspace.sources[default_index]
    for axis_index in range(len(designspace.axes)):
        positions = [i.axes[axis_index] for i in font.instances]
        designspace.axes[axis_index].map = None
        designspace.axes[axis_index].maximum = max(positions)
        designspace.axes[axis_index].minimum = min(positions)
        designspace.axes[axis_index].default = next(
            i.axes[axis_index] for i in font.instances if isinstance(i.weight, str)
        )
    instantiator = Instantiator.from_designspace(designspace)
    ufos.extend(instantiator.generate_instance(i) for i in designspace.instances)
    return ufos

def add_math_table(font: GSFont, input: str, output: str=None):
    if not output:
        output = input
    math_glyph_info = get_math_glyph_info(font)
    tt_font = TTFont(input)
    tt_font['MATH'] = math_table(tt_font, math_glyph_info['Regular'])
    tt_font.save(output)
    tt_font.close()

def get_math_glyph_info(font: GSFont) -> dict:
    math_glyph_info = {master.name: {
        'MathItalicsCorrectionInfo': {},
        'MathTopAccentAttachment': {},
        'ExtendedShapeCoverage': {},
        'MathKernInfo': {},
    } for master in font.masters}
    for glyph in font.glyphs:
        for layer in (l for l in glyph.layers if l.name in math_glyph_info):
            def _set_info(plist_key, key):
                math_glyph_info[layer.name][key][glyph.name] = next(
                    data[plist_key] for data in layer.userData if plist_key in data)
            try:
                _set_info('italicCorrection', 'MathItalicsCorrectionInfo')
                _set_info('topAccent', 'MathTopAccentAttachment')
            except StopIteration:
                pass
    return math_glyph_info

def eprint(*values):
    print(*values, file=sys.stderr)

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        if self.name:
            eprint(self.name)
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        eprint('Elapsed: {:.3}s\n'.format(time.time() - self.start_time))

def build(input: str, output_dir: str):
    '''Build fonts from Glyphs source.

    1. Read the `.glyphspackage` directory into a `GSFont` object with preprocessing
    2. Convert the `GSFont` into a list of UFO objects and perform interpolation
    3. Generate `.otf` font files
    4. Add the OpenType MATH tables
    '''
    eprint('Python {}\nfonttools {}\nglyphsLib {}\n'.format(
        sys.version.split()[0],
        fontTools.version,
        glyphsLib.__version__,
    ))

    # Phase 1
    with Timer('Parsing input file \'{}\'...'.format(input)):
        font = read_glyphs_package(input)
        fix_export(font)
        decompose_smart_comp(font)

    # Phase 2
    with Timer('Generating UFO...'):
        ufos = to_ufos(font)

    # Phase 3
    with Timer('Generating OTF...'):
        FontProject(verbose='WARNING').build_otfs(ufos, output_dir=output_dir)

    # Phase 4
    with Timer('Adding MATH table...'):
        # TODO: We only do it for the regular weight now.
        add_math_table(font, input='build/FiraMath-Regular.otf')
        # add_math_table(
        #     font,
        #     input='build/FiraMath-Regular.otf',
        #     output='build/FiraMath-math-Regular.otf',
        # )

if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', output_dir='build/')
