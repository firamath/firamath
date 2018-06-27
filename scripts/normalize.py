#!/usr/bin/python
"""A simple python script for sfd normalization. It will do the following jobs:

- Sort the glpyhs with unicode order (in unicode block) or the order defined in `non-unicode.txt`
  (not in unicode block).
- Rename glyphs as `uniXXXX` or `uXXXX`.
- Check unused glpyhs (i.e. in the font but not defined in `non-unicode.txt`, or vice versa).

This script requires `otfcc` for otf -> JSON serialization.
"""

from __future__ import print_function

import glob
import json
import os
import platform
import re

# For debug only.
# import sys

CWD = os.getcwd()
if platform.system() == "Linux":
    OTFCC = CWD + "/lib/otfcc/bin/release-x64/otfccdump"
elif platform.system() == "Windows":
    OTFCC = "otfccdump"

# RE patterns.
# Groups:                        1            2   3             4     5     6
ENCODING_PATTERN = re.compile(r"(StartChar: )(.+)(\nEncoding: )(\S+) (\S+) (\S+)\n")
# Groups:                     1        2     3     4
REFER_PATTERN = re.compile(r"(Refer: )(\S+) (\S+) ([NS])")

# Other constants
NON_UNICODE_BEGIN_INDEX = 1114112 # 1114112 = 0x110000 is the beginning of non-unicode block
NON_UNICODE_CODE_POINT = -1

def get_glyph_meta_data(family_name, weight_list, non_unicode_data, otf_path, json_path):
    """Each element in `meta_data_list` should be a list of dict:
    `{"encoding": e, "unicode": u, "index": i, "name": n}`.
    """
    meta_data_list = []
    for weight in weight_list:
        font_name = family_name + "-" + weight.capitalize()
        font_otf = otf_path + font_name + ".otf"
        font_json = json_path + font_name + ".json"
        otfcc_dump(font_otf, font_json)
        unicode_glyphs = get_unicode_glyph_meta_data(font_json)
        non_unicode_glyphs = get_non_unicode_glyph_meta_data(
            font_json, non_unicode_data,
            begin_index=len(unicode_glyphs),
            show_info=True)
        meta_data_list.append(unicode_glyphs + non_unicode_glyphs)
    return meta_data_list

def otfcc_dump(otf_file, json_file):
    """Use `otfcc` library for JSON serialization.
    """
    run_process(OTFCC, ["--pretty", "-o", json_file, otf_file])

def run_process(cmd, args):
    """Run `cmd` with `args`. Spaces will be added automatically.
    """
    cmd_line = cmd
    for i in args:
        cmd_line += (" " + i)
    os.system(cmd_line)

def get_unicode_glyph_meta_data(json_file_name, begin_index=0):
    """Return a list of meta data dict for glyphs in unicode block.
    """
    with open(json_file_name, "r") as json_file:
        encoding_list = sorted([int(i) for i in json.load(json_file)["cmap"].keys()])
    return [
        {"encoding": v, "unicode": v, "index": begin_index + i, "name": make_glyph_name(v)}
        for i, v in enumerate(encoding_list)
    ]

def make_glyph_name(unicode_dec):
    """
    Arg:
        `unicode_dec`: unicode integer (decimal)
    Return:
        `uXXXXX` if `hex` >= 0x10000, `uniXXXX` if `hex` < 0x10000.
    """
    u_hex_str = hex(unicode_dec)[2:].upper() # Remove `0x` and capitalize.
    str_len = len(u_hex_str)
    if str_len == 5:
        return "u" + u_hex_str
    if str_len == 4:
        return "uni" + u_hex_str
    if str_len == 3:
        return "uni0" + u_hex_str
    if str_len == 2:
        return "uni00" + u_hex_str

def get_non_unicode_glyph_meta_data(
        json_file,
        non_unicode_data_file,
        begin_index=0,
        show_info=True):
    """Return a list of meta data dict for glyphs NOT in unicode block.

    Args:
        `begin_index`: it should be the number of unicode glyphs.
        `show_info`:   whether print debug information.
    """
    glyph_list_from_json = get_non_unicode_from_json(json_file)
    glyph_list_from_data = get_non_unicode_from_data(non_unicode_data_file)
    # Get the intersection of `glyph_list_from_json` and `glyph_list_from_data`.
    # The glyphs' order should be the same as in `glyph_list_from_data`.
    glyph_list = [i for i in glyph_list_from_data if i in glyph_list_from_json]
    if show_info:
        for i in glyph_list_from_json:
            if not i in glyph_list:
                print("Warning: Glyph \"" + i + "\" in JSON will be ignored.")
        for i in glyph_list_from_data:
            if not i in glyph_list:
                print("Warning: Glyph \"" + i + "\" in \"non-unicode.txt\" will be ignored.")
    return [
        {
            "encoding": NON_UNICODE_BEGIN_INDEX + i,
            "unicode": NON_UNICODE_CODE_POINT,
            "index": begin_index + i,
            "name": v
        }
        for i, v in enumerate(glyph_list)
    ]

def get_non_unicode_from_json(json_file_name):
    """Return a list of non-unicode glyph names from JSON.
    """
    with open(json_file_name, "r") as json_file:
        json_data = json.load(json_file)
    return [i for i in json_data["glyph_order"] if not i in json_data["cmap"].values()]

def get_non_unicode_from_data(data_file_name):
    """Return a list of non-unicode glyph names from JSON.
    """
    with open(data_file_name, "r") as data_file:
        return [line.strip() for line in data_file if not line.startswith(";")]

# Add underline
def normalize_file_name(file_name):
    """Normalize glyph file name.

    When `file_name` is begin with `u` rather than `uni`, there should be an extra
    `_` before the last letter.
    """
    return re.sub(r"^(u[^n].*)(\D)$", r"\1_\2", file_name)

def update_glyph_files(meta_data_list, family_name_full, weight_list, sfd_path):
    """Use the data in `meta_data_list` to normalize glyphs.
    """
    for weight, meta_data in zip(weight_list, meta_data_list):
        if platform.system() == "Linux":
            sfdir = sfd_path + family_name_full + "-" + weight + ".sfdir/"
        elif platform.system() == "Windows":
            sfdir = sfd_path + family_name_full + "-" + weight + ".sfdir\\"
        glyph_file_list = glob.glob(sfdir + "*.glyph") + glob.glob(sfdir + ".notdef.glyph")
        # Read glyph files.
        glyph_content_list = []
        for glyph_file_name in glyph_file_list:
            with open(glyph_file_name, "r") as glyph_file:
                glyph_content_list.append(glyph_file.read())
        # We need the old meta data to update `Refer`.
        old_meta_data = [get_single_glyph_meta_data(i) for i in glyph_content_list]
        # Get the new glyph file names and contents.
        new_glyph_file_list = []
        new_glyph_content_list = []
        for i in glyph_content_list:
            (name, content) = replace_meta_data(i, meta_data)
            content = replace_refer(content, old_meta_data, meta_data)
            new_glyph_file_list.append(sfdir + name)
            new_glyph_content_list.append(content)
        # Delete old files then write new files.
        delete_files(glyph_file_list)
        write_files(new_glyph_file_list, new_glyph_content_list)
        print("Processing " + family_name_full + "-" + weight + " finished!")

def get_single_glyph_meta_data(glyph_content):
    """Get meta data dict from a single glyph file.
    """
    search_result = re.search(ENCODING_PATTERN, glyph_content)
    return {
        "encoding": int(search_result.group(4)),
        "unicode":int(search_result.group(5)),
        "index": int(search_result.group(6)),
        "name": search_result.group(2)
    }

def replace_meta_data(glyph_content, new_meta_data_list):
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
    file_name = normalize_file_name(new_meta_data["name"]) + ".glyph"
    return (file_name, re.sub(ENCODING_PATTERN, new_meta_str, glyph_content))

def replace_refer(glyph_content, old_meta_data_list, new_meta_data_list):
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

def write_files(file_list, content_list):
    """Write files in `file_list` with the content in `content_list`.
    """
    for i, content in zip(file_list, content_list):
        if platform.system() == "Linux":
            with open(i, "w") as file_i:
                file_i.write(content)
        elif platform.system() == "Windows":
            with open(i, "w", newline="\n") as file_i:
                file_i.write(content)

def delete_files(file_list):
    """Delete all files in `file_list`.
    """
    for i in file_list:
        os.remove(i)

def main():
    """The main function.
    """
    # Directories and files.
    if platform.system() == "Linux":
        sfd_path = CWD + "/src/"
        otf_path = CWD + "/docs/assets/"
        data_path = CWD + "/data/"
        json_path = CWD + "/data/"
    elif platform.system() == "Windows":
        sfd_path = CWD + "\\src\\"
        otf_path = CWD + "\\docs\\assets\\"
        data_path = CWD + "\\data\\"
        json_path = CWD + "\\data\\"
    non_unicode_data = data_path + "non-unicode.txt"
    # Font meta data.
    family_name = "FiraMath"
    family_name_full = "fira-math"
    weight_list = ["thin", "light", "regular", "medium", "bold"]
    # For debug
    # weight_list = ["regular"]
    # sfd_path = "./temp/"

    # The core procedure.
    meta_data_list = get_glyph_meta_data(family_name, weight_list, non_unicode_data,
                                         otf_path, json_path)
    update_glyph_files(meta_data_list, family_name_full, weight_list, sfd_path)

if __name__ == "__main__":
    main()
