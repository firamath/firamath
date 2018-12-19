#!/usr/bin/python
"""Interpolate intermediate weights from several basic styles.
"""

from __future__ import print_function

import collections
import json
import os
import fontforge as ff


WEIGHT_LIST = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular"]
with open(os.sep.join([os.getcwd(), "data", "weight-analysis.json"])) as f:
    WEIGHT_ANALYSIS_DATA = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)


def _open_font(weight):
    file_name = os.sep.join([os.getcwd(), "src", "FiraMath-" + weight + ".sfd"])
    return ff.open(file_name)


# def _transpose(_list):
#     return map(list, zip(*_list))


# def _name_to_unicode(char_name):
#     if "." in char_name:
#         return -1
#     if "uni" in char_name:
#         return int(char_name[4:], 16)
#     if "u" in char_name:
#         return int(char_name[1:], 16)


def interpolate_font(weight_dict, glyph_list):
    font_list = [_open_font(weight) for weight in weight_dict.keys()]
    font_a, font_b = font_list[0], font_list[-1]
    t_list = weight_dict.values()

    for glyph_name in glyph_list:
        for font, t in zip(font_list[1:-1], t_list[1:-1]):
            if glyph_name in font:
                print("Glyph <" + glyph_name + "> is already in " + font.fontname +
                      ". Will be removed.")
                font.removeGlyph(glyph_name)
            font.createInterpolatedGlyph(font_a[glyph_name], font_b[glyph_name], t)
            font.save()


if __name__ == "__main__":
    integral_glyphs = [
        "uni222B.display",
        "uni222C.display",
        "uni222D.display",
        "uni2A0C.display"]
    interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], integral_glyphs)
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], integral_glyphs)
