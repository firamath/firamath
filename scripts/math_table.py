#!/usr/bin/python
"""Modify OpenType MATH table for Fira Math.

See https://docs.microsoft.com/typography/opentype/spec/math#mathconstants-table.
"""

from __future__ import print_function

import os
import sys

import fontforge as ff

sys.path.append(os.path.sep.join([os.getcwd(), os.path.dirname(__file__)]))
from _common import *


def _parse_json():
    with open(MATH_TABLE_JSON_FILE_NAME) as f:
        return comment_json_loads(f.read())
MATH_TABLE = _parse_json()


def _get_math_constants():
    """Generate the MATH constants for all weights.
    """
    def _interpolation(_v1, _v2, k):
        return int(_v1 + k * (_v2 - _v1))
    result = {}
    for name, value in MATH_TABLE["MathConstants"].items():
        coeff_dict = {}
        for weight, coeff in WEIGHT_ANALYSIS_DATA["Thin-Regular"].items():
            coeff_dict[weight] = _interpolation(value[0], value[1], coeff)
        for weight, coeff in WEIGHT_ANALYSIS_DATA["Regular-Ultra"].items():
            coeff_dict[weight] = _interpolation(value[1], value[2], coeff)
        result[name] = coeff_dict
    return result
MATH_CONSTANTS_DICT = _get_math_constants()


def add_math_table(font):
    _add_math_constants(font)
    _add_math_glyph_info(font, MATH_TABLE["MathGlyphInfo"])
    _add_math_variants(font, MATH_TABLE["MathVariants"])


def _add_math_constants(font):
    for name, value in MATH_CONSTANTS_DICT.items():
        exec("font.math." + name + " = " + str(value[font.weight]))


def _add_math_glyph_info(font, math_glyph_info_dict):
    pass


def _add_math_variants(font, math_variants_dict):
    pass




######### TODO #########
######### To be removed!

def add_variants(font, variants_dict, variant_type):
    """Add vertical/horizontal variants.
    """
    for glyph_name in variants_dict:
        _check_glyph_name(font, glyph_name)
        if variant_type == "vertical":
            font[glyph_name].verticalVariants = variants_dict[glyph_name]
        elif variant_type == "horizontal":
            font[glyph_name].horizontalVariants = variants_dict[glyph_name]
    font.save()


def _check_glyph_name(font, glyph_name, fallback_glyph=0x0020):
    """The glyph with `glyph_name` will be created as `default_glyph` if not exists.

    Defalut value of `fallback_glyph` is U+0020 SPACE.
    """
    glyph_unicode = glyph_name_to_unicode(glyph_name)
    if glyph_name not in font:
        font.createChar(glyph_unicode, glyph_name)
        font.selection.select(fallback_glyph)
        font.copy()
        font.selection.select(glyph_name)
        font.paste()

def _main():
    weight_lists = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular", "Medium",
                    "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]
    # weight_lists = ["Thin", "Regular", "Ultra"]
    integral_glyphs = {
        "uni222B": "uni222B uni222B.display",
        "uni222C": "uni222C uni222C.display",
        "uni222D": "uni222D uni222D.display",
        "uni2A0C": "uni2A0C uni2A0C.display",
        "uni222E": "uni222E uni222E.display",
        "uni222F": "uni222F uni222F.display",
        "uni2230": "uni2230 uni2230.display"}
    font_list = [open_font(weight) for weight in weight_lists]
    for font in font_list:
        add_vertical_variants(font, integral_glyphs)

if __name__ == "__main__":
    add_math_table(0)
    # _main()
