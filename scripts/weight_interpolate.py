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
    ## 2019-01-06  Integrals (I)
    # integral_glyphs = [
    #     # Normal integrals
    #     "uni222B.display", "uni222C.display", "uni222D.display", "uni2A0C.display",
    #     # Contour integrals
    #     "uni222E.display", "uni222F.display", "uni2230.display"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], integral_glyphs)
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], integral_glyphs)

    ## 2019-01-31 Summations and products (I)
    # sum_prod_glyphs = [
    #     "uni2140", "uni220F", "uni2210", "uni2211",
    #     "uni2140.display", "uni220F.display", "uni2210.display", "uni2211.display"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], sum_prod_glyphs)
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], sum_prod_glyphs)

    ## 2019-02-02  Primes
    # prime_glyphs = ["uni2032", "uni2033", "uni2034", "uni2057", "uni2035", "uni2036", "uni2037"]
    # prime_glyphs += ([glyph + ".ssty1" for glyph in prime_glyphs] +
    #                  [glyph + ".ssty2" for glyph in prime_glyphs])
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Ultra"], prime_glyphs)

    ## 2019-02-04 Summations and products (II)
    # sum_prod_glyphs = ["uni2140", "uni220F", "uni2210", "uni2211"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], sum_prod_glyphs)
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], sum_prod_glyphs)

    ## 2019-02-05  Integrals (II)
    # integral_glyphs = ["uni222B", "uni222C", "uni222D", "uni2A0C"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], integral_glyphs)
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], integral_glyphs)

    ## 2019-02-06  Binaries (I)
    # binary_glyphs = ["uni00B1", "uni2212", "uni2213", "uni2214"]
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], binary_glyphs)
    # interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], binary_glyphs)

    ## 2019-02-06  Arrows (I)
    arrow_glyphs = ["uni" + hex(0x2190 + i)[2:].upper() for i in range(112)]
    interpolate_font(WEIGHT_ANALYSIS_DATA["Thin-Regular"], arrow_glyphs)
    interpolate_font(WEIGHT_ANALYSIS_DATA["Regular-Ultra"], arrow_glyphs)
