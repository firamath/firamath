#!/usr/bin/python
"""A simple python script for sfd normalization.
"""

import os
import glob
import json
import re

# For debug only.
import sys

# Directories and files
pwd              = os.getcwd()
sfd_path         = pwd + "/src/"
otf_path         = pwd + "/docs/assets/"
data_path        = pwd + "/data/"
json_path        = pwd + "/data/"
otfcc            = pwd + "/lib/otfcc/bin/release-x64/otfccdump"
non_unicode_data = data_path + "non-unicode.txt"

# Font meta data
family_name      = "FiraMath"
family_name_full = "fira-math"
# weights          = ["thin", "light", "regular", "medium", "bold"]
weights          = ["regular"]

# Other constants
NON_UNICODE_BEGIN_INDEX = 1114112 # 1114112 = 0x110000 is the beginning of non-unicode block
NON_UNICODE_CODE_POINT = -1

#class GlyphMetaData:
#    """
#    The metadata of a glyph, including encodings, index and glyph name etc.
#    """
#    def __init__(self):
#        self.encoding = 0
#        self.unicode = 0
#        self.index = 0
#        self.name = ""

def get_glyph_meta_data():
    cmap = []
    for i in weights:
        font_name = family_name + "-" + i.capitalize()
        font_otf = otf_path + font_name + ".otf"
        font_json = json_path + font_name + ".json"
        otfcc_dump(font_otf, font_json)
        unicode_glyphs = get_unicode_glyph_meta_data(font_json)
        non_unicode_glyphs = get_non_unicode_glyph_meta_data(
            font_json, non_unicode_data,
            begin_index=len(unicode_glyphs),
            show_info=True)
        cmap.append(unicode_glyphs + non_unicode_glyphs)
        #for i in unicode_glyphs + non_unicode_glyphs:
        #    print(i)
        #sys.exit(0)
    return cmap

def otfcc_dump(otf_file, json_file):
    """Use `otfcc` library for JSON serialization.
    """
    run_process(otfcc, ["--pretty", "-o", json_file, otf_file])

def run_process(cmd, args):
    """Run `cmd` with `args`. Spaces will be added automatically.
    """
    cmd_line = cmd
    for i in args:
        cmd_line += (" " + i)
    os.system(cmd_line)

def get_unicode_glyph_meta_data(json_file, begin_index=0):
    with open(json_file, "r") as json_file:
        encoding_list = sorted([int(i) for i in json.load(json_file)["cmap"].keys()])
    return [
        {"encoding": v, "unicode":v, "index": begin_index + i, "name": make_glyph_name(v)}
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
    """
    Return a list of `GlyphMetaData` for glpyhs NOT in unicode block.
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
    return re.sub(r"^(u[^n].*)(\D)$", r"\1_\2", file_name)

#####################
# 1st dimension: weight
# 2nd dimension: sorted by index
# 3rd dimension: (<encoding dec>, <unicode dec>, <glyph index dec>, <glyph name>)
cmap = get_glyph_meta_data()
print(cmap)
sys.exit(0)

#                                1            2   3             4     5     6
encoding_pattern = re.compile(r"(StartChar: )(.+)(\nEncoding: )(\S+) (\S+) (\S+)\n")

refer_pattern = re.compile(r"Refer: (\S+) (\S+) ([NS])")

# #HACK
# sfd_path = "./temp/"

for i, v in enumerate(weights):
    sfdir = sfd_path + family_name_full + "-" + v + ".sfdir/"
    glyph_files = glob.glob(sfdir + "*.glyph")
    new_glyph_files = []
    for glyph_file in glyph_files:
        with open(glyph_file, "r") as f:
            glyph_content = f.read()

        m = re.match(encoding_pattern, glyph_content)
        unicode_idx = m.group(5) # The 2nd number in `encoding`
        glyph_idx   = m.group(6) # The 3rd number in `encoding`
        glyph_name  = m.group(2)

        if unicode_idx != "-1":
            e = next((x for x in cmap[i] if x[1] == int(unicode_idx)), None)
        else:
            e = next((x for x in cmap[i] if x[3] == glyph_name), None)
        meta = m.group(1) + e[3] + \
               m.group(3) + str(e[0]) + " " + str(e[1]) + " " + str(e[2]) + "\n"

        new_file_name = sfdir + normalize_file_name(e[3]) + ".glyph"
        new_content = re.sub(encoding_pattern, meta, glyph_content)
        new_glyph_files.append((new_file_name, new_content))

    # !!!!!!!!!!!!!!!!!!!!!!!
    for glyph_file in glyph_files:
        os.remove(glyph_file)

    for new_glyph_file in new_glyph_files:
        with open(new_glyph_file[0], "w") as f:
            f.write(new_glyph_file[1])
    print("Processing " + family_name_full + "-" + v + " finished!")
