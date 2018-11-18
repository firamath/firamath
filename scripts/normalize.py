#!/usr/bin/python
"""A simple python script for FontForge SFD normalization. It will do the following jobs:

- Discard GUI information.
- Sort the glpyhs.
- Rename glyphs as `uniXXXX` or `uXXXX`.

See: https://fontforge.github.io/sfdformat.html
     https://github.com/libertinus-fonts/libertinus/blob/master/tools/sfdnormalize.py

WARNING: `Refer` info is not considered in this script!
"""

from __future__ import print_function
from __future__ import unicode_literals

import csv
import io
import os
import re

SFD_PATTERN = re.compile(r"^(.*)BeginChars\S*\n*(.*)EndChars", flags=re.DOTALL)
DROP_PATTERN = re.compile(
    r"(?:UComments|sfntRevision|Compacted|DisplaySize|FitToEm|ModificationTime|WinInfo):\s.*\n")
SINGLE_CHAR_PATTERN = re.compile(
    r"""StartChar:\s*(\S*)\n*Encoding:\s*([-\d]+)\s*([-\d]+)\s*([-\d]+)\n(.+?)EndChar""",
    flags=re.DOTALL)
FLAG_PATTERN = re.compile(r"(Flags:\s).*\n")
HINT_PATTERN = re.compile(r"[HVD]Stem2?:\s.*\n")
MASK_PATTERN = re.compile(r"(\s[mcl]\s)(\d)(?:x?.*)\n")
DROP_REPL = ""
FLAG_REPL = r"\1W\n"
HINT_REPL = ""
# `0x4` means that the point is selected
MASK_REPL = lambda mask_match: mask_match.group(1) + str(int(mask_match.group(2)) % 0x4) + "\n"

CSV_GLYPH_NAME_INDEX = 1
CSV_STATUS_INDEX = 5
CSV_STATUS_VALID_TUPLE = ("A", "A/C")

NON_UNICODE_BEGIN_ENCODING = 0x110000
NON_UNICODE_CODE_POINT = -1

CWD = os.getcwd()
SFD_PATH = os.sep.join([CWD, "src"])
CSV_FILE_NAME = os.sep.join([CWD, "data", "glyph-stats.csv"])
FONT_FAMILY_NAME = "FiraMath"
WEIGHT_LIST = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
               "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]


class Char:
    """Descript a single char/glyph in SFD file.
    """
    _prefix_dict = {5: "u", 4: "uni", 3: "uni0", 2: "uni00"}

    def __init__(self, name, encoding, _unicode, index=None, data=""):
        self.name = name
        self.encoding = encoding
        self.unicode = _unicode
        self.index = index
        self.data = data
        self._name_normalize()
        self._data_normalize()

    def _name_normalize(self):
        """The `name` will be `uXXXXX` if `hex` >= 0x10000, `uniXXXX` if `hex` < 0x10000.
        """
        if self.is_unicode():
            unicode_hex_str = hex(self.unicode)[2:].upper()  # Remove `0x` and capitalize
            self.name = self._prefix_dict[len(unicode_hex_str)] + unicode_hex_str
        return self

    def _data_normalize(self):
        """Normalize `Flags`, stem hints and masks in `SplineSet`.
        """
        self.data = re.sub(FLAG_PATTERN, FLAG_REPL, self.data)
        self.data = re.sub(HINT_PATTERN, HINT_REPL, self.data)
        self.data = re.sub(MASK_PATTERN, MASK_REPL, self.data)
        return self

    def encoding_index_normalize(self, new_index, non_unicode_begin_index):
        """Update `encoding` and index`.
        """
        if not self.is_unicode():
            self.encoding = NON_UNICODE_BEGIN_ENCODING + new_index - non_unicode_begin_index
        self.index = new_index
        return self

    def is_unicode(self):
        """Check if this `Char` is unicode or not.
        """
        if self.unicode != NON_UNICODE_CODE_POINT:
            return True
        return False


def get_name_list(csv_file_name):
    """Return a list of glyph names from font data file (CSV).
    """
    with open(csv_file_name, "r") as csv_file:
        csv_reader = csv.reader(csv_file)
        return [row[CSV_GLYPH_NAME_INDEX] for row in csv_reader
                if row[CSV_STATUS_INDEX] in CSV_STATUS_VALID_TUPLE]


def sfd_parse(sfd_file_name):
    """Read and parse the `.sfd` file. Return a dict of `head` string and `chars` list.
    """
    with open(sfd_file_name, "r") as sfd_file:
        sfd_str = sfd_file.read()
    sfd_head_str, sfd_chars_str = re.findall(SFD_PATTERN, sfd_str)[0]
    sfd_chars_list = [Char(name=i[0], encoding=int(i[1]), _unicode=int(i[2]), data=i[4])
                      for i in re.findall(SINGLE_CHAR_PATTERN, sfd_chars_str)]
    return {"head": sfd_head_str, "chars": sfd_chars_list}


def sfd_write(sfd_file_name, sfd_str, backup=False):
    """Write `sfd_str` into SFD file.
    """
    def _write(file_name, content):
        with io.open(file_name, "w", newline="\n") as sfd_file:
            sfd_file.write(content)
    if backup:
        with open(sfd_file_name, "r") as sfd_file:
            bak_sfd_str = sfd_file.read()
        _write(sfd_file_name + ".bak", bak_sfd_str)
    _write(sfd_file_name, sfd_str)


def sfd_normalize(sfd, name_list):
    """Normalize the whole SFD file.
    """
    # Head
    sfd_head_str = _sfd_head_normalize(sfd["head"])
    # Chars
    sfd_chars_list = _sfd_chars_normalize(sfd["chars"], name_list)
    sfd_chars_str = "\n\n".join(
        [("StartChar: " + char.name + "\n" +
          "Encoding: " + " ".join(map(str, (char.encoding, char.unicode, char.index))) + "\n" +
          char.data + "EndChar") for char in sfd_chars_list])
    # Begin/end chars
    sfd_capacity = str(max(sfd_chars_list[-1].encoding + 1, NON_UNICODE_BEGIN_ENCODING))
    sfd_length = str(len(sfd_chars_list))
    sfd_begin_chars_str = ("BeginChars: " + sfd_capacity + " " + sfd_length + "\n\n")
    sfd_end_chars_str = "\nEndChars\nEndSplineFont\n"
    return sfd_head_str + sfd_begin_chars_str + sfd_chars_str + sfd_end_chars_str


def _sfd_head_normalize(sfd_head_str):
    return re.sub(DROP_PATTERN, DROP_REPL, sfd_head_str)


def _sfd_chars_normalize(sfd_chars_list, name_list):
    name_index_dict = {v: i for i, v in enumerate(name_list)}
    non_unicode_begin_index = len([char for char in sfd_chars_list if char.is_unicode()])
    return [char.encoding_index_normalize(i, non_unicode_begin_index)
            for i, char in enumerate(
                sorted(sfd_chars_list, key=lambda i: name_index_dict[i.name]))]


def _main():
    for i in WEIGHT_LIST:
        file_name = os.sep.join([SFD_PATH, FONT_FAMILY_NAME + "-" + i + ".sfd"])
        sfd = sfd_parse(file_name)
        sfd_str = sfd_normalize(sfd, get_name_list(CSV_FILE_NAME))
        # sfd_write(file_name, sfd_str, backup=True)
        sfd_write(file_name, sfd_str)


if __name__ == "__main__":
    _main()
