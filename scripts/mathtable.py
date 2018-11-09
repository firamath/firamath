#!/usr/bin/python
"""Modify OpenType MATH table for Fira Math.

See https://docs.microsoft.com/typography/opentype/spec/math#mathconstants-table.
"""

import collections
import io
import os
import re


CWD = os.getcwd()
SFD_PATH = os.sep.join([CWD, "src"])
FONT_FAMILY_NAME = "FiraMath"
WEIGHT_LIST = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
               "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]

MATH_TABLE_PATTERN = re.compile(r"MATH:.+(Encoding: UnicodeFull\n)", flags=re.DOTALL)
MATH_TABLE_END_PATTERN = re.compile(r"(Encoding: UnicodeFull\n)")

MATH_CONSTANTS = collections.OrderedDict({
    # General
    "ScriptPercentScaleDown": [80],
    "ScriptScriptPercentScaleDown": [60],
    "DelimitedSubFormulaMinHeight": [1500],
    "DisplayOperatorMinHeight": [1500],
    "MathLeading": [150],
    "AxisHeight": [280],
    "AccentBaseHeight": [527],
    "FlattenedAccentBaseHeight": [689],
    # Sub/Superscript
    "SubscriptShiftDown": [350],
    "SubscriptTopMax": [527],
    "SubscriptBaselineDropMin": [250],
    "SuperscriptShiftUp": [400],
    "SuperscriptShiftUpCramped": [270],
    "SuperscriptBottomMin": [130],
    "SuperscriptBaselineDropMax": [360],
    "SubSuperscriptGapMin": [200],
    "SuperscriptBottomMaxWithSubscript": [527],
    "SpaceAfterScript": [41],
    # Limits
    "UpperLimitGapMin": [150],
    "UpperLimitBaselineRiseMin": [150],
    "LowerLimitGapMin": [150],
    "LowerLimitBaselineDropMin": [600],
    # Stacks
    "StackTopShiftUp": [450],
    "StackTopDisplayStyleShiftUp": [580],
    "StackBottomShiftDown": [480],
    "StackBottomDisplayStyleShiftDown": [700],
    "StackGapMin": [200],
    "StackDisplayStyleGapMin": [500],
    "StretchStackTopShiftUp": [300],
    "StretchStackBottomShiftDown": [600],
    "StretchStackGapAboveMin": [150],
    "StretchStackGapBelowMin": [150],
    # Fractions
    "FractionNumeratorShiftUp": [450],
    "FractionNumeratorDisplayStyleShiftUp": [580],
    "FractionDenominatorShiftDown": [480],
    "FractionDenominatorDisplayStyleShiftDown": [700],
    "FractionNumeratorGapMin": [80],
    "FractionNumeratorDisplayStyleGapMin": [200],
    "FractionRuleThickness": [76],
    "FractionDenominatorGapMin": [80],
    "FractionDenominatorDisplayStyleGapMin": [200],
    "SkewedFractionHorizontalGap": [0],
    "SkewedFractionVerticalGap": [0],
    # Over/Underbars
    "OverbarVerticalGap": [150],
    "OverbarRuleThickness": [66],
    "OverbarExtraAscender": [50],
    "UnderbarVerticalGap": [150],
    "UnderbarRuleThickness": [66],
    "UnderbarExtraDescender": [50],
    # Radicals
    "RadicalVerticalGap": [96],
    "RadicalDisplayStyleVerticalGap": [142],
    "RadicalRuleThickness": [76],
    "RadicalExtraAscender": [76],
    "RadicalKernBeforeDegree": [276],
    "RadicalKernAfterDegree": [-400],
    "RadicalDegreeBottomRaisePercent": [64],
    # Connectors
    "MinConnectorOverlap": [20]
})

MATH_CONSTANTS_INT_KEYS = [
    "ScriptPercentScaleDown",
    "ScriptScriptPercentScaleDown",
    "DelimitedSubFormulaMinHeight",
    "DisplayOperatorMinHeight",
    "RadicalDegreeBottomRaisePercent",
    "MinConnectorOverlap"
]


def sfd_read(sfd_file_name):
    with open(sfd_file_name, "r") as sfd_file:
        return sfd_file.read()


def sfd_write(sfd_file_name, sfd_str, backup=False):
    """Write `sfd_str` into SFD file.
    """
    def _write(file_name, content):
        with io.open(file_name, "w", newline="\n") as sfd_file:
            sfd_file.write(content)
    if backup:
        with open(sfd_file_name, "r") as sfd_file:
            bak_sfd_str = sfd_file.read()
        _write(sfd_file_name + ".bak", bak_sfd_str)
    _write(sfd_file_name, sfd_str)


def get_math_table_str():
    math_table_entries = [
        "MATH:" + key + ": " + str(value[0]) + (" " if key not in MATH_CONSTANTS_INT_KEYS else "")
        for key, value in MATH_CONSTANTS.items()]
    return "\n".join(math_table_entries)


def add_math_table(sfd_file_name, math_table_str):
    sfd_str = re.sub(MATH_TABLE_PATTERN, r"\1", sfd_read(sfd_file_name))
    sfd_str = re.sub(MATH_TABLE_END_PATTERN, math_table_str + r"\n\1", sfd_str)
    sfd_write(sfd_file_name, sfd_str)


def _main():
    math_table_str = get_math_table_str()
    for i in WEIGHT_LIST:
        file_name = os.sep.join([SFD_PATH, FONT_FAMILY_NAME + "-" + i + ".sfd"])
        add_math_table(file_name, math_table_str)


if __name__ == "__main__":
    _main()
