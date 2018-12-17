"""Constants and functions for accessing glyph data of Fira Math.
"""

import csv
import os


FILE_NAME = os.sep.join([os.getcwd(), "data", "glyph-stats.csv"])

UNICODE_INDEX = 0
UNICODE_NAME_INDEX = 1
GLYPH_NAME_INDEX = 2
ADOBE_CHAR_INDEX = 3
UNICODE_BLOCK_INDEX = 4
NON_UNICODE_TYPE_INDEX = 5
STATUS_INDEX = 6
SOURCE_INDEX = 7
FIRA_GLYPH_INDEX = 8
INTERPOLATION_INDEX = 9

STATUS_VALID_TUPLE = ("A", "A/C")
SOURCE_VALID_TUPLE = ("R", "B", "I", "X")
INTERPOLATION_VALID_TUPLE = ("3", )


def get_name_list():
    """Return a list of glyph names from font data file (CSV).
    """
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        return [row[GLYPH_NAME_INDEX] for row in reader
                if row[STATUS_INDEX] in STATUS_VALID_TUPLE]


def _unicode_str_to_int(unicode_str):
    """`unicode_str` should be `"U+XXXX"` or `"U+XXXXX"`.
    """
    return int(unicode_str[2:], 16)


def get_mapping_dict():
    """Return a dict of glyph mappings from font data file (CSV). Each entry is in the format:
        unicode<int>: {"source": R/B/I/X, "fira-glyph": <int>}.
    """
    def _key(row):
        return _unicode_str_to_int(row[UNICODE_INDEX])

    def _val(row):
        fira_glyph_str = row[FIRA_GLYPH_INDEX]
        if fira_glyph_str == "":
            fira_glyph = _unicode_str_to_int(row[UNICODE_INDEX])
        else:
            if fira_glyph_str[:2] == "U+":
                fira_glyph = _unicode_str_to_int(fira_glyph_str)
            else:
                fira_glyph = fira_glyph_str
        return {"source": row[SOURCE_INDEX], "fira-glyph": fira_glyph}

    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        return {_key(row): _val(row) for row in reader
                if row[SOURCE_INDEX] in SOURCE_VALID_TUPLE}


def get_interpolation_list():
    """Return a list of glyph names that need to be interpolated.
    """
    with open(FILE_NAME, "r") as file:
        reader = csv.reader(file)
        return [row[GLYPH_NAME_INDEX] for row in reader
                if row[INTERPOLATION_INDEX] in INTERPOLATION_VALID_TUPLE]
