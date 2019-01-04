#!/usr/bin/python
"""Modify OpenType MATH table for Fira Math.

TODO: ONLY DRAFT NOW!

See https://docs.microsoft.com/typography/opentype/spec/math#mathconstants-table.
"""

from __future__ import print_function

import os
import fontforge as ff


def _open_font(weight):
    file_name = os.sep.join([os.getcwd(), "src", "FiraMath-" + weight + ".sfd"])
    return ff.open(file_name)


def _name_to_unicode(name):
    if "." in name:
        return -1
    if "uni" in name:
        return int(name[3:], 16)
    if "u" in name:
        return int(name[1:], 16)


def _main():
    weight_lists = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular", "Medium",
                    "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]
    # weight_lists = ["Thin", "Regular", "Ultra"]
    integral_glyphs = {
        "uni222B": "uni222B uni222B.display",
        "uni222C": "uni222C uni222C.display",
        "uni222D": "uni222D uni222D.display",
        "uni2A0C": "uni2A0C uni2A0C.display",
        "uni222E": "uni222E uni222E.display",
        "uni222F": "uni222F uni222F.display",
        "uni2230": "uni2230 uni2230.display"}
    font_list = [_open_font(weight) for weight in weight_lists]
    for font in font_list:
        for glyph_name in integral_glyphs.keys():
            glyph_unicode = _name_to_unicode(glyph_name)
            if glyph_name not in font:
                font.createChar(glyph_unicode, glyph_name)
                font.selection.select(0x0020)  # Space
                font.copy()
                font.selection.select(glyph_name)
                font.paste()
            font[glyph_name].verticalVariants = integral_glyphs[glyph_name]
        font.save()

if __name__ == "__main__":
    _main()
