'''Build FiraMath.glyphspackage.
'''

import os
import re
import sys
from typing import OrderedDict, List

from fontTools.ttLib import TTFont

# We use https://github.com/googlefonts/glyphsLib/pull/652 to support Glyphs3
sys.path.insert(0, 'lib')

from glyphsLib import GSFont
from glyphsLib.parser import Parser
from glyphsLib.writer import Writer
from glyphsLib.builder import to_ufos

from fontmake.font_project import FontProject

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

def build(input: str, output_dir: str):
    eprint('Parsing input file \'{}\'...'.format(input))
    input_font = read_glyphs_package(input)

    eprint('\nParsing to UFO...')
    temp_glyphs = os.path.join(output_dir, os.path.splitext(os.path.basename(input))[0] + '.glyphs')
    with open(temp_glyphs, 'w') as f:
        Writer(f).write(input_font)
    with open(temp_glyphs, 'r') as f:
        font: GSFont = Parser(current_type=GSFont).parse(f.read())
    os.remove(temp_glyphs)
    ufos = to_ufos(font)

    eprint('\nExporting...')
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
