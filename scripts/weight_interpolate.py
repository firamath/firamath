"""Interpolate intermediate weights from several basic styles.
"""

from __future__ import print_function

import collections
import json
import os
import fontforge as ff


with open(os.sep.join([os.getcwd(), "data", "weight-analysis.json"])) as f:
    WEIGHT_ANALYSIS_DATA = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)


def _open_font(weight):
    file_name = os.sep.join([os.getcwd(), "src", "FiraMath-" + weight + ".sfd"])
    return ff.open(file_name)


def interpolate_font(weight_dict, glyph_list):
    font_list = [_open_font(weight) for weight in weight_dict.keys()]
    font_a, font_b = font_list[0], font_list[-1]
    t_list = weight_dict.values()

    for font, t in zip(font_list[1:-1], t_list[1:-1]):
        for glyph_name in glyph_list:
            if glyph_name in font:
                print("Glyph <" + glyph_name + "> is already in " + font.fontname +
                      ". Will be removed.")
                font.removeGlyph(glyph_name)
            font.createInterpolatedGlyph(font_a[glyph_name], font_b[glyph_name], t)
            font[glyph_name].removeOverlap()
            font[glyph_name].round()
        font.save()


if __name__ == "__main__":
    ## 2019-05-08 Geometry (I)
    circle_glyphs = [
        "uni22C5", "uni2219", "u1F784", "uni2022", "uni2981", "uni26AB", "uni25CF", "uni2B24",
        "uni2218", "uni25E6", "uni26AC", "uni26AA", "uni25CB", "uni25EF"]
    interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], circle_glyphs)
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], circle_glyphs)
