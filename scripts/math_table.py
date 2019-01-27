"""Modify OpenType MATH table for Fira Math.

See https://docs.microsoft.com/typography/opentype/spec/math.
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
    # Add MATH constants.
    for name, value in MATH_CONSTANTS_DICT.items():
        exec("font.math." + name + " = " + str(value[font.weight]))
    _add_math_glyph_info(font, MATH_TABLE["MathGlyphInfo"])
    # Add MATH variants.
    _add_math_variants(font, "horizontalVariants")
    _add_math_variants(font, "verticalVariants")


def _add_math_glyph_info(font, math_glyph_info_dict):
    # TODO
    pass


def _add_math_variants(font, variants_type):
    for _glyph, _var in MATH_TABLE["MathVariants"][variants_type].items():
        glyph, var = str(_glyph), str(" ".join(_var))  # Convert unicode to raw string
        if glyph in font:
            exec("font[glyph]." + variants_type + " = var")
