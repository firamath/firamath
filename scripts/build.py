'''Build FiraMath.glyphspackage.
'''

import copy
import os
import re
import sys
from typing import OrderedDict, List

from fontmake.font_project import FontProject
from fontTools.ttLib import TTFont
from glyphsLib import GSFont, GSGlyph, GSLayer, GSNode, GSPath
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

def decompose_smart_componets(font: GSFont):
    for glyph in font.glyphs:
        if '_smart.' not in glyph.name: # TODO:
            for layer in glyph.layers:
                master_id: str = layer.associatedMasterId
                to_be_removed = []
                for comp in layer.components:
                    if value_dict := comp.smartComponentValues:
                        eprint('Decomposing smart componets in {}'.format(glyph))
                        ref_glyph: GSGlyph = comp.component
                        to_be_removed.append(comp)
                        paths = get_smart_component_paths(master_id, ref_glyph, value_dict)
                        layer.paths.extend(paths)
                layer._shapes = [s for s in layer._shapes if s not in to_be_removed]

def get_smart_component_paths(master_id: str, glyph: GSGlyph, value_dict: dict) -> List[GSPath]:
    if len(value_dict) != 1:
        raise ValueError('We only support single smart component axis!')
    key, value = next(iter(value_dict.items()))
    interpolation_value = next(
        rescale(value, axis.bottomValue, axis.topValue)
        for axis in glyph.smartComponentAxes if axis.name == key
    )
    is_part_n = lambda layer, n: \
        layer.associatedMasterId == master_id and layer.partSelection[key] == n
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


def build(input: str, output_dir: str):
    # Phase 1
    # Read the .glyphspackage file as an OrderedDict.
    eprint('Parsing input file \'{}\'...'.format(input))
    input_font = read_glyphs_package(input)

    # Phase 2
    # Write to a temp .glyphs files, then read it again as a GSFont object.
    # At this stage, the smart components will also be decomposed.
    # Finally, the GSFont object will be turned into a UFO object.
    eprint('\nParsing to UFO...')
    temp_glyphs = os.path.join(output_dir, os.path.splitext(os.path.basename(input))[0] + '.glyphs')
    with open(temp_glyphs, 'w') as f:
        Writer(f).write(input_font)
    with open(temp_glyphs, 'r') as f:
        font: GSFont = Parser(current_type=GSFont).parse(f.read())
    decompose_smart_componets(font)
    os.remove(temp_glyphs)
    ufos = to_ufos(font)

    # Phase 3
    # Generate .otf font files.
    # TODO: The MATH table will be added.
    eprint('\nGenerating OTF...')
    FontProject(verbose='WARNING').save_otfs(ufos, output_dir=output_dir)

def add_math_table(path: str):
    eprint('\nAdding MATH table...')
    font = TTFont(path)
    font['MATH'] = math_table(font)
    font.save(path)
    font.close()

def eprint(values):
    print(values, file=sys.stderr)

if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', output_dir='build/')
    add_math_table('build/FiraMath-Regular.otf')
