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
    result = {}
    for name, value in MATH_TABLE["MathConstants"].items():
        value_dict = {}
        for weight, coeff in WEIGHT_ANALYSIS_DATA["Thin-Regular"].items():
            value_dict[weight] = _interpolate(value[0], value[1], coeff)
        for weight, coeff in WEIGHT_ANALYSIS_DATA["Regular-Ultra"].items():
            value_dict[weight] = _interpolate(value[1], value[2], coeff)
        result[name] = value_dict
    return result
def _interpolate(_v1, _v2, k):
    return int(_v1 + k * (_v2 - _v1))
MATH_CONSTANTS_DICT = _get_math_constants()


def _get_math_components():
    return {i: _get_math_comp_aux_a(i)
            for i in ("verticalComponents", "horizontalComponents")}
def _get_math_comp_aux_a(comp_type):
    comp_dict = {}
    for weight, coeff in WEIGHT_ANALYSIS_DATA["Thin-Regular"].items():
        comp_dict[weight] = _get_math_comp_aux_b(comp_type, coeff, 0, 1)
    for weight, coeff in WEIGHT_ANALYSIS_DATA["Regular-Ultra"].items():
        comp_dict[weight] = _get_math_comp_aux_b(comp_type, coeff, 1, 2)
    return comp_dict
def _get_math_comp_aux_b(comp_type, coeff, pos_1, pos_2):
    return {str(name): _get_math_comp_aux_c(comp, coeff, pos_1, pos_2)
            for name, comp in MATH_TABLE["MathVariants"][comp_type].items()}
def _get_math_comp_aux_c(comp, coeff, pos_1, pos_2):
    return tuple(tuple([str(i["name"]), int(i["isExtender"])]
                       + _get_math_comp_aux_d(i, coeff, pos_1, pos_2))
                 for i in comp)
def _get_math_comp_aux_d(comp_i, coeff, pos_1, pos_2):
    return [_interpolate(comp_i[i][pos_1], comp_i[i][pos_2], coeff)
            for i in ["startConnectorLength", "endConnectorLength", "fullAdvance"]]
MATH_COMPONENTS = _get_math_components()


def add_math_table(font):
    # Add MATH constants.
    for name, value in MATH_CONSTANTS_DICT.items():
        exec("font.math." + name + " = " + str(value[font.weight]))
    _add_math_glyph_info(font, MATH_TABLE["MathGlyphInfo"])
    # Add MATH variants and components.
    _add_math_variants(font, "verticalVariants")
    _add_math_variants(font, "horizontalVariants")
    _add_math_components(font, "verticalComponents")
    _add_math_components(font, "horizontalComponents")


def _add_math_glyph_info(font, math_glyph_info_dict):
    # TODO
    pass


def _add_math_variants(font, variants_type):
    for _glyph, _var in MATH_TABLE["MathVariants"][variants_type].items():
        glyph, var = str(_glyph), str(" ".join(_var))  # Convert unicode to raw string
        if glyph in font:
            exec("font[glyph]." + variants_type + " = var")


def _add_math_components(font, components_type):
    for glyph, comp in MATH_COMPONENTS[components_type][font.weight].items():
        if glyph in font:
            exec("font[glyph]." + components_type + " = comp")
