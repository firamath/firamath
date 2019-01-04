#!/usr/bin/python
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

    for glyph_name in glyph_list:
        for font, t in zip(font_list[1:-1], t_list[1:-1]):
            if glyph_name in font:
                print("Glyph <" + glyph_name + "> is already in " + font.fontname +
                      ". Will be removed.")
                font.removeGlyph(glyph_name)
            font.createInterpolatedGlyph(font_a[glyph_name], font_b[glyph_name], t)
            font.save()


if __name__ == "__main__":
    # 2018-12-22
    # prime_glyphs = [
    #     "uni2032",
    #     "uni2033",
    #     "uni2034",
    #     "uni2057",
    #     "uni2035",
    #     "uni2036",
    #     "uni2037",
    #     "uni2032.ssty1",
    #     "uni2033.ssty1",
    #     "uni2034.ssty1",
    #     "uni2057.ssty1",
    #     "uni2035.ssty1",
    #     "uni2036.ssty1",
    #     "uni2037.ssty1",
    #     "uni2032.ssty2",
    #     "uni2033.ssty2",
    #     "uni2034.ssty2",
    #     "uni2057.ssty2",
    #     "uni2035.ssty2",
    #     "uni2036.ssty2",
    #     "uni2037.ssty2"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Ultra"], prime_glyphs)

    # 2019-01-04
    integral_glyphs = [
        # Normal integrals
        "uni222B.display",
        "uni222C.display",
        "uni222D.display",
        "uni2A0C.display",
        # Contour integrals
        "uni222E.display",
        "uni222F.display",
        "uni2230.display"]
    interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], integral_glyphs)
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], integral_glyphs)
