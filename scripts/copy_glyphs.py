"""Copy glyphs from FiraSans. The weight mapping is as the following:

    + Thin          ExtraLight
      UltraLight    Light
      ExtraLight    Book
      Light         Regular
      Book          Medium
    + Regular       Bold
      Medium        ExtraBold
      SemiBold      Heavy
    + Bold          Ultra
      ExtraBold     -
      Heavy         -
    + Ultra         -

Here, `+` denotes the masters, `-` means no bold versions are available.
"""

from __future__ import print_function

import os
import fontforge

import glyph_data

SOURCE_FONT_FAMILY_NAME = "FiraSans"
FONT_FAMILY_NAME = "FiraMath"
FONT_FAMILY_FULL_NAME = "Fira Math"

WEIGHT_LIST_A = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
                 "Medium", "SemiBold", "Bold"]
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
# WEIGHT_DICT = {"master_1": ["Thin", "Regular", "Bold"],
#                "master_2": ["Ultra"],
#                "inter_1":  ["UltraLight", "ExtraLight", "Light", "Book"],
#                "inter_2":  ["Medium", "SemiBold"],
#                "inter_3":  ["ExtraBold", "Heavy"]}

CWD = os.getcwd()
OTF_PATH = os.sep.join([CWD, "assets", "Fira_Sans_OTF_4301", "Normal"])
SFD_PATH = os.sep.join([CWD, "temp", "sfd", "new"])


def open_font(weight, copy_bold=True):
    """Open font with corresponding variant styles. Return a dict as:
        R/B/I/X: <font object>.
    """
    def _italic(w):
        return "Italic" if w == "Regular" else w + "Italic"
    if copy_bold:
        styles = {"R": ("Roman", weight),
                  "B": ("Roman", WEIGHT_MAPPING_DICT[weight]),
                  "I": ("Italic", _italic(weight)),
                  "X": ("Italic", _italic(WEIGHT_MAPPING_DICT[weight]))}
    else:
        styles = {"R": ("Roman", weight), "I": ("Italic", _italic(weight))}
    return {key: fontforge.open(os.sep.join(
        [OTF_PATH, val[0], SOURCE_FONT_FAMILY_NAME + "-" + val[1] + ".otf"]))
            for key, val in styles.items()}


def initialize_font(weight):
    """Create a new font, with constans initialized.
    """
    font = fontforge.font()
    font.fontname = FONT_FAMILY_NAME + "-" + weight
    font.fullname = FONT_FAMILY_FULL_NAME + " " + weight
    font.familyname = FONT_FAMILY_FULL_NAME
    font.weight = weight
    font.encoding = "UnicodeFull"
    font.copyright = ""
    font.version = ""
    font.comment = None
    return font


def copy_glyphs(target_font, source_font_tuple, mapping_dict):
    source_font = source_font_tuple[mapping_dict["source"]]
    source_font.selection.select(mapping_dict["fira-glyph"])
    source_font.copy()
    target_font.selection.select(mapping_dict["unicode"])
    target_font.paste()


def _split_list(x, func):
    """Split the list into maximum ordered list, while the remaining elements are left as
    single element lists. E.g.
        [3, 4, 5, 6, 2, 3, 4] -> [[3, 4, 5, 6], [2], [3], [4]]
    """
    def _find_last_sorted_pos(_list):
        for i in range(len(_list) - 1):
            if func(_list[i]) >= func(_list[i + 1]):
                return i
        return len(_list) - 1
    last_sorted_pos = _find_last_sorted_pos(x)
    return [x[:last_sorted_pos + 1]] + [[x[i]] for i in range(last_sorted_pos + 1, len(x))]


def _main():
    mapping_dict = glyph_data.get_mapping_dict()
    source_font_dict = {i: open_font(i) for i in WEIGHT_LIST_A}
    source_font_dict.update({i: open_font(i, copy_bold=False) for i in WEIGHT_LIST_B})
    for weight, val in source_font_dict.items():
        new_font = initialize_font(weight)
        for style in val.keys():
            # FontForge's selection will ignore the selection order, so we need to find the max
            # ordered list to speed up. The remaining glyphs will be selected one-by-one.
            mapping_list = [(i, v["fira-glyph"])
                            for i, v in mapping_dict.items() if v["source"] == style]
            mapping_list.sort(key=lambda _tuple: _tuple[0])
            for i in _split_list(mapping_list, lambda _tuple: _tuple[1]):
                mapping_keys, mapping_values = tuple(zip(*i))
                source_font = val[style]
                source_font.selection.select(*mapping_values)
                source_font.copy()
                new_font.selection.select(*mapping_keys)
                new_font.paste()

        new_font_file_name = os.sep.join([SFD_PATH, FONT_FAMILY_NAME + "-" + weight + ".sfd"])
        new_font.save(new_font_file_name)
    for font in fontforge.fonts():
        font.close()

if __name__ == "__main__":
    # Usage (redirect stderr to file):
    #   ffpython .\scripts\copy.py >con: 2>[file]
    _main()
