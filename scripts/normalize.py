#!/usr/bin/python
"""A simple python script for SFDIR normalization. It will do the following jobs:

- Sort the glpyhs with unicode order (in unicode block) or the order defined in `non-unicode.txt`
  (not in unicode block).
- Rename glyphs as `uniXXXX` or `uXXXX`.
- Check unused glpyhs (i.e. in the font but not defined in `non-unicode.txt`, or vice versa).
"""

from __future__ import print_function

import glob
import os
import platform
import re

CWD = os.getcwd()

# RE patterns.
# Groups:                        1            2   3             4     5     6
ENCODING_PATTERN = re.compile(r"(StartChar: )(.+)(\nEncoding: )(\S+) (\S+) (\S+)\n")
# Groups:                     1        2     3     4
REFER_PATTERN = re.compile(r"(Refer: )(\S+) (\S+) ([NS])")

# Other constants
NON_UNICODE_BEGIN_ENCODING = 0x110000
NON_UNICODE_CODE_POINT = -1

def _get_non_unicode_data(file_name):
    with open(file_name, "r") as f:
        return [line.strip() for line in f if not line.startswith(";")]

def _get_glyph_data(path):
    def _read_glyph_file(file_name):
        with open(file_name, "r") as f:
            return f.read()
    return [_read_glyph_file(i) for i in _get_glyph_file_list(path)]

def _get_glyph_file_list(path):
    return glob.glob(os.path.join(path, "*.glyph")) + [os.path.join(path, ".notdef.glyph")]

def _get_meta_data(glyph_data, non_unicode_data):
    old_meta_data = [_get_single_meta_data(i) for i in glyph_data]
    new_meta_data = _update_meta_data(old_meta_data, non_unicode_data)
    return {"old": old_meta_data, "new": new_meta_data}

def _get_single_meta_data(glyph_content):
    search_result = re.search(ENCODING_PATTERN, glyph_content)
    return {
        "encoding": int(search_result.group(4)),
        "unicode": int(search_result.group(5)),
        "index": int(search_result.group(6)),
        "name": search_result.group(2)
    }

def _update_meta_data(old_meta_data, non_unicode_data):
    # Unicode block
    unicode_list = sorted([i["unicode"] for i in old_meta_data if i["unicode"] != -1])
    unicode_meta_data = [{
        "encoding": v,
        "unicode": v,
        "index": i,
        "name": _make_glyph_name(v)
    } for i, v in enumerate(unicode_list)]
    # Non-unicode block
    raw_non_unicode_list = [i["name"] for i in old_meta_data if i["unicode"] == -1]
    non_unicode_list = []
    for i in non_unicode_data:
        if i in raw_non_unicode_list:
            non_unicode_list.append(i)
        else:
            print("Warning: Glyph \"" + i + "\" in \"non-unicode.txt\" will be ignored.")
    # non_unicode_list = [i for i in non_unicode_data if i in raw_non_unicode_list]
    non_unicode_meta_data = [{
        "encoding": NON_UNICODE_BEGIN_ENCODING + i,
        "unicode": NON_UNICODE_CODE_POINT,
        "index": len(unicode_meta_data) + i,
        "name": v
    } for i, v in enumerate(non_unicode_list)]
    # Result
    return unicode_meta_data + non_unicode_meta_data

def _make_glyph_name(unicode_dec):
    """Return `uXXXXX` if `hex` >= 0x10000, `uniXXXX` if `hex` < 0x10000.
    """
    unicode_hex_str = hex(unicode_dec)[2:].upper() # Remove `0x` and capitalize.
    prefix_dict = {5: "u", 4: "uni", 3: "uni0", 2: "uni00"}
    return prefix_dict[len(unicode_hex_str)] + unicode_hex_str

def _update_sfd(path, glyph_data, meta_data):
    new_glyph_data = _update_glyph_data(glyph_data, meta_data)
    _clear_sfd(path)
    _write_sfd(path, new_glyph_data)

def _update_glyph_data(glyph_data, meta_data):
    new_glyph_data = []
    for i in glyph_data:
        (name, content) = _replace_meta_data(i, meta_data["new"])
        content = _replace_refer(content, meta_data["old"], meta_data["new"])
        new_glyph_data.append({"file_name": name, "content": content})
    return new_glyph_data

def _replace_meta_data(glyph_content, new_meta_data_list):
    """Return the new file name and the new meta data.
    """
    encoding_search = re.search(ENCODING_PATTERN, glyph_content)
    unicode_str = encoding_search.group(5)
    glyph_name = encoding_search.group(2)
    # Search in `new_meta_data_list`.
    # Unicode glyphs will be identified with unicode,
    # while non-unicode glyphs will be identified with glyph name.
    if unicode_str != "-1":
        new_meta_data = next(
            (x for x in new_meta_data_list if x["unicode"] == int(unicode_str)), None)
    else:
        new_meta_data = next(
            (x for x in new_meta_data_list if x["name"] == glyph_name), None)
    new_meta_str = encoding_search.group(1) + new_meta_data["name"] + \
                   encoding_search.group(3) + str(new_meta_data["encoding"]) + " " + \
                                              str(new_meta_data["unicode"]) + " " + \
                                              str(new_meta_data["index"]) + "\n"
    file_name = _normalize_file_name(new_meta_data["name"]) + ".glyph"
    return (file_name, re.sub(ENCODING_PATTERN, new_meta_str, glyph_content))

def _normalize_file_name(file_name):
    """Normalize glyph file name, i.e. add underlines.

    When `file_name` is begin with `u` rather than `uni`, there should be an extra
    `_` before the last letter.
    """
    if file_name == ".notdef" or "." not in file_name:
        file_name_base, file_name_ext = file_name, ""
    else:
        file_name_base, file_name_ext = file_name.split(".", 1)
        file_name_ext = "." + file_name_ext
    return re.sub(r"^(u[^n].*)(\D)$", r"\1_\2", file_name_base) + file_name_ext

def _replace_refer(glyph_content, old_meta_data_list, new_meta_data_list):
    """Return the new `Refer` meta data.
    """
    refer_search = re.search(REFER_PATTERN, glyph_content)
    if refer_search != None:
        refer_index_str = refer_search.group(2)
        refer_unicode_str = refer_search.group(3)
        old_refer = next(
            (x for x in old_meta_data_list if x["index"] == int(refer_index_str)), None)
        if refer_unicode_str != "-1":
            new_refer = next(
                (x for x in new_meta_data_list if x["unicode"] == int(refer_unicode_str)), None)
        else:
            new_refer = next(
                (x for x in new_meta_data_list if x["name"] == old_refer["name"]), None)
        new_refer_str = refer_search.group(1) + \
            str(new_refer["index"]) + " " + \
            str(new_refer["unicode"]) + " " + \
            refer_search.group(4)
        return re.sub(REFER_PATTERN, new_refer_str, glyph_content)
    else:
        return glyph_content

def _clear_sfd(path):
    for i in _get_glyph_file_list(path):
        os.remove(i)

def _write_sfd(path, new_glyph_data):
    for i in new_glyph_data:
        file_name = os.path.join(path, i["file_name"])
        if platform.system() == "Linux":
            with open(file_name, "w") as f:
                f.write(i["content"])
        elif platform.system() == "Windows":
            with open(file_name, "w", newline="\n") as f:
                f.write(i["content"])

def _main():
    src_path = os.path.join(CWD, "src")
    non_unicode_data_file = os.path.join(CWD, "data", "firamath-non-unicode.txt")
    family_name = "FiraMath"
    weight_list = ["Thin", "Light", "Regular", "Medium", "Bold"]
    # For debug
    weight_list = ["Regular"]

    # Core procedure.
    non_unicode_data = _get_non_unicode_data(non_unicode_data_file)
    for weight in weight_list:
        sfd_path = os.path.join(src_path, family_name + "-" + weight + ".sfdir")
        glyph_data = _get_glyph_data(sfd_path)
        meta_data = _get_meta_data(glyph_data, non_unicode_data)
        _update_sfd(sfd_path, glyph_data, meta_data)
        print("Info: Processing " + family_name + "-" + weight + " finished!")

if __name__ == "__main__":
    _main()
