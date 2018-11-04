#!/usr/bin/python
"""A simple python script for FontForge SFD normalization. It will do the following jobs:

- Discard GUI information.
- Sort the glpyhs.
- Rename glyphs as `uniXXXX` or `uXXXX`.

WARNING: `Refer` info is not considered in this script!
"""

from __future__ import print_function

import csv
import platform
import re

SFD_PATTERN = r"^(.*)BeginChars\S*\n*(.*)EndChars"
SINGLE_CHAR_PATTERN = r"""StartChar:\s*(\S*)\n*
                          Encoding:\s*([-\d]+)\s*([-\d]+)\s*([-\d]+)\n
                          (.+?)
                          EndChar"""
DROP_PATTERN = re.compile(r"((?:WinInfo|DisplaySize|ModificationTime):\s).*")
DROP_REPL = r"\1"

CSV_GLYPH_NAME_INDEX = 1
CSV_STATUS_INDEX = 6
CSV_STATUS_VALID_TUPLE = ("A", "A/C", "D")

NON_UNICODE_BEGIN_ENCODING = 0x110000
NON_UNICODE_CODE_POINT = -1


class Char:
    """Descript a single char/glyph in SFD file.
    """
    _prefix_dict = {5: "u", 4: "uni", 3: "uni0", 2: "uni00"}

    def __init__(self, name, encoding, unicode, index=None, data=""):
        self.name = name
        self.encoding = encoding
        self.unicode = unicode
        self.index = index
        self.data = data

    def name_normalize(self):
        """The `name` will be `uXXXXX` if `hex` >= 0x10000, `uniXXXX` if `hex` < 0x10000.
        """
        if self.is_unicode():
            unicode_hex_str = hex(self.unicode)[2:].upper()  # Remove `0x` and capitalize
            self.name = self._prefix_dict[len(unicode_hex_str)] + unicode_hex_str
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
        sfd_content_str = sfd_file.read()
    sfd_head_str, sfd_chars_str = re.findall(SFD_PATTERN, sfd_content_str, flags=re.DOTALL)[0]
    sfd_chars_list = [
        Char(name=i[0], encoding=int(i[1]), unicode=int(i[2]), data=i[4])
        for i in re.findall(SINGLE_CHAR_PATTERN, sfd_chars_str, flags=re.DOTALL + re.VERBOSE)]
    return {"head": sfd_head_str, "chars": sfd_chars_list}


def _sfd_head_normalize(sfd_head_str):
    return re.subn(DROP_PATTERN, DROP_REPL, sfd_head_str)[0]


def _sfd_chars_normalize(sfd_chars_list, name_list):
    name_index_dict = {v: i for i, v in enumerate(name_list)}
    non_unicode_begin_index = len([char for char in sfd_chars_list if char.is_unicode()])
    result = [char.name_normalize() for char in sfd_chars_list]
    result.sort(key=lambda i: name_index_dict[i.name])
    return [char.encoding_index_normalize(i, non_unicode_begin_index)
            for i, char in enumerate(result)]


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
    sfd_begin_chars_str = ("BeginChars: " + str(sfd_chars_list[-1].encoding + 1) + " " +
                           str(len(sfd_chars_list)) + "\n\n")
    sfd_end_chars_str = "\nEndChars\nEndSplineFont\n"

    return sfd_head_str + sfd_begin_chars_str + sfd_chars_str + sfd_end_chars_str


def sfd_write(sfd_file_name, sfd_str):
    """Write `sfd_str` into SFD file.
    """
    if platform.system() == "Linux":
        with open(sfd_file_name, "w") as sfd_file:
            sfd_file.write(sfd_str)
    elif platform.system() == "Windows":
        with open(sfd_file_name, "w", newline="\n") as sfd_file:
            sfd_file.write(sfd_str)


def _main():
    # TODO
    sfd = sfd_parse(_file_name)
    sfd_str = sfd_normalize(sfd, get_name_list(_csv_file_name))
    sfd_write(_file_name, sfd_str)


if __name__ == "__main__":
    _main()
