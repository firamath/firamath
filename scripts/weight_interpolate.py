"""Interpolate intermediate weights from several basic styles.
"""

import collections
import json
import os
import fontforge as ff


with open(os.sep.join([os.getcwd(), "data", "weight-analysis.json"])) as f:
    WEIGHT_ANALYSIS_DATA = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)


def _open_font(weight: str):
    file_name = os.sep.join([os.getcwd(), "src", "FiraMath-" + weight + ".sfd"])
    return ff.open(file_name)


def interpolate_font(weights: dict, glyph: list):
    font_list = [_open_font(weight) for weight in weights.keys()]
    font_a, font_b = font_list[0], font_list[-1]
    t_list = list(weights.values())

    for font, t in zip(font_list[1:-1], t_list[1:-1]):
        for glyph_name in glyph:
            if glyph_name in font:
                print("Glyph <" + glyph_name + "> is already in " + font.fontname +
                      ". Will be removed.")
                font.removeGlyph(glyph_name)
            font.createInterpolatedGlyph(font_a[glyph_name], font_b[glyph_name], t)
            font[glyph_name].removeOverlap()
            font[glyph_name].round()
        font.save()


def interpolate_font_all(glyphs: list):
    interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], glyphs)
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], glyphs)


if __name__ == "__main__":
    ## 2019-06-22 Arrows (III)
    arrow_glyphs_1 = ["uni21DC", "uni21DD", "uni21F4"]
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], arrow_glyphs_1)
    arrow_glyphs_2 = (
        ["uni" + hex(0x27F0 + i)[2:].upper() for i in range(16)]  # Supplemental Arrows-A
      + ["uni290A", "uni290B"]                                    # Supplemental Arrows-B
      + ["uni2B30", "uni2B32", "uni2B33", "uni2B45", "uni2B46"])  # Miscellaneous Symbols and Arrows
    interpolate_font_all(arrow_glyphs_2)
