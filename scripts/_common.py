"""Common constants and functions for building Fira Math.
"""

import collections
import json
import os
import re

import fontforge as ff


FONT_FAMILY_NAME = "FiraMath"
FONT_FAMILY_FULL_NAME = "Fira Math"

WEIGHT_LIST = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
               "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]
# Weights that have bold alphabets.
WEIGHT_LIST_A = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
                 "Medium", "SemiBold", "Bold"]
# Weights that have no bold alphabets.
WEIGHT_LIST_B = ["ExtraBold", "Heavy", "Ultra"]

WEIGHT_MAPPING_DICT = {"Thin":       "ExtraLight",
                       "UltraLight": "Light",
                       "ExtraLight": "Book",
                       "Light":      "Regular",
                       "Book":       "Medium",
                       "Regular":    "Bold",
                       "Medium":     "ExtraBold",
                       "SemiBold":   "Heavy",
                       "Bold":       "Ultra"}

# Paths.
SFD_PATH  = os.sep.join([os.getcwd(), "src"])
DATA_PATH = os.sep.join([os.getcwd(), "data"])

MATH_TABLE_JSON_FILE_NAME = os.sep.join([DATA_PATH, "math-table.json"])
WEIGHT_ANALYSIS_JSON_FILE_NAME = os.sep.join([DATA_PATH, "weight-analysis.json"])


def open_font(weight):
    """Open SFD font file with FontForge.
    """
    file_name = os.sep.join([SFD_PATH, FONT_FAMILY_NAME + "-" + weight + ".sfd"])
    return ff.open(file_name)


def glyph_name_to_unicode(name):
    """Get the character's Unicode from its name.

    The `name` can be either `uniXXXX`, `uXXXXX` or `XXXX.YYYY`.
    """
    if "." in name:
        return -1
    if "uni" in name:
        return int(name[3:], 16)
    if "u" in name:
        return int(name[1:], 16)


def comment_json_loads(json_string, *args):
    """Load JSON with comments.
    """
    json_string = re.sub(r"//.*$", "", json_string, flags=re.MULTILINE)
    return json.loads(json_string, *args)


def _weight_analysis_data():
    """Return weight analysis data as `OrderedDict`.
    """
    with open(WEIGHT_ANALYSIS_JSON_FILE_NAME) as f:
        return json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
WEIGHT_ANALYSIS_DATA = _weight_analysis_data()
