'''Build FiraMath.glyphspackage.
'''

import copy
import os
import sys
import time

from fontmake.font_project import FontProject
from fontmake.instantiator import Instantiator

import fontTools
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.ttFont import newTable

import glyphsLib
from glyphsLib import GSComponent, GSFont, GSGlyph, GSLayer, GSNode, GSPath
from glyphsLib.parser import Parser

import toml

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

def add_math_table(font: GSFont, toml_path: str, input_dir: str, output_dir: str=None):
    if not output_dir:
        output_dir = input_dir
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # TODO: For masters only
    masters = sorted(font.masters, key=lambda m: m.weightValue)
    font_name = font.familyName.replace(' ', '')
    style_names = [master.name for master in masters]

    data = toml.load(toml_path)

    for style_index, style_name in enumerate(style_names):
        math_table = otTables.MATH()
        math_table.Version = 0x00010000
        math_table.MathConstants = math_constants(style_index, data['MathConstants'])
        math_table.MathGlyphInfo = math_glyph_info(font, style_index)
        math_table.MathVariants = math_variants(font, style_index, data['MathVariants'])

        font_file_name = '{}-{}.otf'.format(font_name, style_name)
        input = os.path.join(input_dir, font_file_name)
        output = os.path.join(output_dir, font_file_name)
        tt_font = TTFont(input)
        tt_font['MATH'] = newTable('MATH')
        tt_font['MATH'].table = math_table
        tt_font.save(output)
        tt_font.close()

def math_constants(style_index: int, data: dict):
    constants = otTables.MathConstants()
    for name, value_dict in data.items():
        value = value_dict['value'][style_index]
        if value_dict['isMathValue']:
            constants.__setattr__(name, math_value(value))
        else:
            constants.__setattr__(name, value)
    return constants

def math_glyph_info(font: GSFont, style_index: int):
    italic_corr_glyphs, italic_corr_values = get_user_data(font, style_index, 'italicCorrection')
    italic_corr = otTables.MathItalicsCorrectionInfo()
    italic_corr.Coverage = coverage(italic_corr_glyphs)
    italic_corr.ItalicsCorrectionCount = len(italic_corr_glyphs)
    italic_corr.ItalicsCorrection = list(map(math_value, italic_corr_values))

    top_accent_glyphs, top_accent_values = get_user_data(font, style_index, 'topAccent')
    top_accent = otTables.MathTopAccentAttachment()
    top_accent.TopAccentCoverage = coverage(top_accent_glyphs)
    top_accent.TopAccentAttachmentCount = len(top_accent_glyphs)
    top_accent.TopAccentAttachment = list(map(math_value, top_accent_values))

    glyph_info = otTables.MathGlyphInfo()
    glyph_info.MathItalicsCorrectionInfo = italic_corr
    glyph_info.MathTopAccentAttachment = top_accent
    glyph_info.ExtendedShapeCoverage = None
    glyph_info.MathKernInfo = None

    return glyph_info

def get_user_data(font: GSFont, style_index: int, key: str):
    glyphs = []
    values = []
    for glyph in font.glyphs:
        for data in (d for d in glyph.layers[style_index].userData if key in d):
            glyphs.append(glyph.name)
            values.append(data[key])
    return glyphs, values

def math_variants(font: GSFont, style_index: int, data: dict):
    variants = otTables.MathVariants()
    variants.MinConnectorOverlap = data['MinConnectorOverlap'][style_index]

    horizontal_variants: dict = data['HorizontalVariants']
    variants.HorizGlyphConstruction = [
        glyph_construction(font, style_index, *item, direction='horizontal')
        for item in horizontal_variants.items()
    ]
    variants.HorizGlyphCoverage = coverage(horizontal_variants.keys())
    variants.HorizGlyphCount = len(horizontal_variants)

    vertical_variants: dict = data['VerticalVariants']
    variants.VertGlyphConstruction = [
        glyph_construction(font, style_index, *item, direction='vertical')
        for item in vertical_variants.items()
    ]
    variants.VertGlyphCoverage = coverage(vertical_variants.keys())
    variants.VertGlyphCount = len(vertical_variants)

    return variants

def glyph_construction(font: GSFont, style_index: int, glyph: str, value: dict, direction: str):
    variants = [glyph + suffix for suffix in value['suffixes']]
    t = otTables.MathGlyphConstruction()
    t.GlyphAssembly = None  # TODO:
    t.VariantCount = len(variants)
    t.MathGlyphVariantRecord = []
    for glyph in variants:
        r = otTables.MathGlyphVariantRecord()
        r.AdvanceMeasurement = advance_measurement(font, style_index, glyph, direction)
        r.VariantGlyph = glyph
        t.MathGlyphVariantRecord.append(r)
    return t

def advance_measurement(font: GSFont, style_index: int, glyph: str, direction: str):
    bounds = font.glyphs[glyph].layers[style_index].bounds
    if direction == 'horizontal':
        return abs(int(bounds.size.width)) + 1
    if direction == 'vertical':
        return abs(int(bounds.size.height)) + 1

def math_value(value):
    t = otTables.MathValueRecord()
    t.DeviceTable = None
    t.Value = value
    return t

def coverage(glyphs):
    c = otTables.Coverage()
    c.glyphs = glyphs
    return c

class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        if self.name:
            print(self.name)
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        print('Elapsed: {:.3}s\n'.format(time.time() - self.start_time))

def build(input_path: str, toml_path: str, output_dir: str):
    '''Build fonts from Glyphs source.

    1. Read the `.glyphspackage` directory into a `GSFont` object with preprocessing
    2. Convert the `GSFont` into a list of UFO objects and perform interpolation
    3. Generate `.otf` font files
    4. Add the OpenType MATH tables
    '''
    print('Python {}\nfonttools {}\nglyphsLib {}\n'.format(
        sys.version.split()[0],
        fontTools.version,
        glyphsLib.__version__,
    ))
    with Timer('Parsing input file \'{}\'...'.format(input_path)):
        font = read_glyphs_package(input_path)
        fix_export(font)
        decompose_smart_comp(font)
    with Timer('Generating UFO...'):
        ufos = to_ufos(font)
    with Timer('Generating OTF...'):
        FontProject(verbose='WARNING').build_otfs(ufos, output_dir=output_dir)
    with Timer('Adding MATH table...'):
        add_math_table(font, toml_path, input_dir=output_dir)

if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', toml_path='src/FiraMath.toml', output_dir='build/')
