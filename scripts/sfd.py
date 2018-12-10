"""SFD format.
"""

import re


class Glyph:
    """A single glyph.

    Members:

        - `name`: the name of the glyph.
        - `splines`: a list of splines.

    Functions:
        - `parse_spline()`: assign values to `splines`.
    """
    # Some RE patterns.
    _GLYPH_PATTERN = re.compile(
        r"StartChar:\s*(\S*)\n(.*?)SplineSet\n(.*?)EndSplineSet.*EndChar", flags=re.DOTALL)
    _EMPTY_GLYPH_PATTERN = re.compile(r"StartChar:\s*(\S*)\n(.*)()EndChar", flags=re.DOTALL)
    _SPLINE_PATTERN = re.compile(r"\s*(.+)\s+m.*?\n(.+)(\1.*?\n)", flags=re.DOTALL)
    _POINT_PATTERM = re.compile(r"\s*(.+)\s+([mcl])\s+(\S+)\n")

    def __init__(self, glyph_str):
        self._str = glyph_str
        self.name, self._header_str, self._spline_str = self._parse()
        self.splines = []

    def _parse(self):
        find_result = re.findall(self._GLYPH_PATTERN, self._str)
        if find_result != []:
            return find_result[0]
        else:
            return re.findall(self._EMPTY_GLYPH_PATTERN, self._str)[0]

    def parse_spline(self):
        def _parse_point(point):
            point_type = point[1]
            coords = tuple(int(x) for x in point[0].split())
            if point_type == "c":
                point_pos = coords[-2:]
                point_control = (coords[0:2], coords[2:4])
            else:
                point_pos = coords
                point_control = None
            return {"type": point_type,
                    "pos": point_pos,
                    "control": point_control,
                    "tag": point[2]}
        spline_list = re.findall(self._SPLINE_PATTERN, self._spline_str)
        for i in spline_list:
            self.splines.append(
                [_parse_point(p) for p in re.findall(self._POINT_PATTERM, i[1] + i[2])])


class SFD:
    """Spline Font Database.

    Members:

        - `path`: the path to the SFD file.
        - `glyphs`: a list of glyphs.
    """
    # Some RE patterns.
    _SFD_PATTERN = re.compile(r"^(SplineFontDB.*BeginChars.*?)\n+(.*)EndChars", flags=re.DOTALL)
    _CHAR_PATTERN = re.compile(r"StartChar.+?EndChar", flags=re.DOTALL)

    def __init__(self, sfd_file_name):
        self.path = sfd_file_name
        with open(self.path, "r") as sfd_file:
            self._str = sfd_file.read()
        self._header_str, self._glyphs_str = re.findall(
            self._SFD_PATTERN, self._str)[0]
        self.glyphs = [Glyph(i) for i in re.findall(self._CHAR_PATTERN, self._glyphs_str)]


def _sfd_test():
    sfd_file_name = os.sep.join([os.getcwd(), "src", "FiraMath-Regular.sfd"])

    start = time.time()
    sfd = SFD(sfd_file_name)
    end = time.time()
    print("> Timing:", end - start, "s")

    start = time.time()
    for i in sfd.glyphs:
        i.parse_spline()
        # print({"Name": i.name, "Header": i._header_str, "Spline": i.splines})
    end = time.time()
    print("> Timing:", end - start, "s")


def _glyph_test():
    glyph_str = """StartChar: uni0026
Encoding: 38 38 6
Width: 729
Flags: W
LayerCount: 2
Fore
SplineSet
302 701 m 0
 411 701 485 636 485 549 c 0
 485 463 419 410 344 366 c 1
 520 200 l 1
 543 247 565 304 580 369 c 1
 666 344 l 1
 641 262 610 197 577 147 c 1
 689 42 l 1
 623 -12 l 1
 526 82 l 1
 470 21 400 -12 305 -12 c 0
 173 -12 81 61 81 175 c 0
 81 262 135 320 220 374 c 1
 161 431 123 477 123 546 c 0
 123 633 186 701 302 701 c 0
303 633 m 0
 245 633 213 596 213 547 c 0
 213 495 244 460 292 415 c 1
 354 453 395 491 395 544 c 0
 395 600 359 633 303 633 c 0
273 324 m 1
 207 281 175 237 175 178 c 0
 175 104 233 61 315 61 c 0
 379 61 428 87 473 133 c 1
 273 324 l 1
EndSplineSet
Validated: 1
EndChar
"""
    glyph = Glyph(glyph_str)
    print([glyph.name])
    print([glyph._spline_str])
    print([glyph._header_str])

    glyph.parse_spline()
    print(glyph.splines)

if __name__ == "__main__":
    import os
    import time
    _glyph_test()
    _sfd_test()
