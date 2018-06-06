#!/usr/bin/python

import os
import json

pwd              = os.getcwd()
sfd_path         = pwd + "/src/"
otf_path         = pwd + "/docs/assets/"
data_path        = pwd + "/data/"
json_path        = pwd + "/data/"
otfcc            = pwd + "/lib/otfcc/bin/release-x64/otfccdump"
family_name      = "FiraMath"
family_name_full = "fira-math"
# weights          = ["thin", "light", "regular", "medium", "bold"]
weights          = ["thin"]
unicode_data     = data_path + "UnicodeData.txt"
non_unicode_data = data_path + "non-unicode.txt"

def run_process(cmd, args):
    cmd_line = cmd
    for i in args:
        cmd_line += (" " + i)
    os.system(cmd_line)

def otfcc_dump(otf_file, json_file):
    run_process(otfcc, ["--pretty", "-o", json_file, otf_file])

def get_unicode_index_from_json(json_file):
    "Return a list of [<dec>, <hex string>] for CMAP from JSON."
    with open(json_file, "r") as f:
        data = json.load(f)["cmap"].keys()
    for idx, item in enumerate(data):
        d = int(item)
        item = (d, hex(d)[2:].upper())
        data[idx] = item
    data.sort(key=lambda x: x[0])
    return data

def get_non_unicode_glyphs_from_json(json_file):
    with open(json_file, "r") as f:
        json_data = json.load(f)
        glyphs_unicode = json_data["cmap"].values()
        glyphs_all = json_data["glyph_order"]
    return set(glyphs_all) - set(glyphs_unicode)

def get_non_unicode_glyphs():
    glyphs_non_unicode = []
    with open(non_unicode_data, "r") as f:
        for line in f:
            s = line.strip()
            if not s.startswith(";"):
                glyphs_non_unicode.append(s)
    return glyphs_non_unicode

def check_non_unicode_glyphs(glyphs_set, glyphs_list, font_name):
    """
    Args:
        `glyphs_set`:  non-unicode glyphs from JSON
        `glyphs_list`: non-unicode glyphs from `non-unicode.txt`
        `font_name`:   name of the font
    """
    result = []
    for i in glyphs_list:
        if i in glyphs_set:
            result.append(i)
        else:
            print("Warning: Glyph \"" + i + "\" not found in " + font_name)
    for i in glyphs_set - set(result):
        print("Warning: Glyph \"" + i + "\" in " + font_name + "not found in \"non-unicode.txt\"")
    return result

def get_unicode_cmap():
    for i in weights:
        font_name = family_name + "-" + i.capitalize()
        font_otf = otf_path + font_name + ".otf"
        font_json = json_path + font_name + ".json"
        #otfcc_dump(font_otf, font_json)

        #data = get_unicode_index_from_json(font_json)
        #print(data[:10])
        data = check_non_unicode_glyphs(get_non_unicode_glyphs_from_json(font_json),
                                 get_non_unicode_glyphs(),
                                 font_name)
        print(data)

# print(pwd)
get_unicode_cmap()
