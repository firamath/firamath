'''Build FiraMath.glyphspackage.
'''

import copy
import os
import re
import sys
from typing import OrderedDict, List

from fontmake.font_project import FontProject
from fontTools.ttLib import TTFont
from glyphsLib import GSComponent, GSFont, GSGlyph, GSLayer, GSNode, GSPath
from glyphsLib.builder import to_ufos
from glyphsLib.parser import Parser
from glyphsLib.writer import Writer

from math_table import math_table

def read_glyphs_package(path: str):
    with open(os.path.join(path, 'fontinfo.plist'), 'r') as fontinfo_plist:
        font: OrderedDict = Parser().parse(fontinfo_plist.read())
    with open(os.path.join(path, 'order.plist'), 'r') as order_plist:
        order: List[str] = Parser().parse(order_plist.read())
    font['glyphs'] = [read_glyph(path, name) for name in order]
    return font

def read_glyph(path: str, name: str):
    file_name = glyph_name_to_file_name(name)
    with open(os.path.join(path, 'glyphs', file_name), 'r') as f:
        return Parser().parse(f.read())

def glyph_name_to_file_name(name: str):
    return ('_notdef' if name == '.notdef' else re.sub(r'([A-Z])', r'\1_', name)) + '.glyph'

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

def decompose(comp: GSComponent) -> List[GSPath]:
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

def get_smart_comp_path(master_id: str, glyph: GSGlyph, value_dict: dict) -> List[GSPath]:
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

def add_math_table(gs_font: GSFont, input: str, output: str=None):
    if not output:
        output = input
    math_glyph_info = get_math_glyph_info(gs_font)
    font = TTFont(input)
    font['MATH'] = math_table(font, math_glyph_info['Regular'])
    font.save(output)
    font.close()

def get_math_glyph_info(font: GSFont) -> dict:
    math_glyph_info = {master.name: {
        'MathItalicsCorrectionInfo': {},
        'MathTopAccentAttachment': {},
        'ExtendedShapeCoverage': {},
        'MathKernInfo': {},
    } for master in font.masters}
    for glyph in font.glyphs:
        for layer in glyph.layers:
            if layer.name in math_glyph_info:
                try:
                    math_glyph_info[layer.name]['MathTopAccentAttachment'][glyph.name] = next(
                        data['topAccent'] for data in layer.userData if 'topAccent' in data)
                except StopIteration:
                    pass
    return math_glyph_info

def build(input: str, output_dir: str):
    '''Build fonts from Glyphs source.

    - Phase 1
        - Read the `.glyphspackage` directory as an `OrderedDict`.
    - Phase 2
        - Write into a temporary `.glyphs` file, and read it again as a `GSFont`.
        - Decompose all the smart components since UFO does not support them.
        - Turn the `GSFont` object into a UFO object.
    - Phase 3
        - Generate `.otf` font files.
        - Add the OpenType MATH tables.
    '''

    # Phase 1
    eprint('Parsing input file \'{}\'...'.format(input))
    input_font = read_glyphs_package(input)

    # Phase 2
    eprint('\nParsing to UFO...')
    temp_glyphs = os.path.join(output_dir, os.path.splitext(os.path.basename(input))[0] + '.glyphs')
    with open(temp_glyphs, 'w') as f:
        Writer(f).write(input_font)
    with open(temp_glyphs, 'r') as f:
        font: GSFont = Parser(current_type=GSFont).parse(f.read())
    fix_export(font)
    decompose_smart_comp(font)
    os.remove(temp_glyphs)
    ufos = to_ufos(font)

    # Phase 3
    eprint('\nGenerating OTF...')
    FontProject(verbose='WARNING').save_otfs(ufos, output_dir=output_dir)
    # TODO: We only do it for the regular weight now.
    eprint('\nAdding MATH table...')
    add_math_table(font, input='build/FiraMath-Regular.otf')

def eprint(values):
    print(values, file=sys.stderr)

if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', output_dir='build/')
