#!/usr/bin/python

import os
import glob
import json
import re

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
weights          = ["thin", "light", "regular", "medium", "bold"]
# weights          = ["thin"]

# Other constants
non_unicode_begin_idx = 1114112 # 1114112 = 0x110000 is the beginning of non-unicode block

def get_cmap():
    cmap = []
    for i in weights:
        font_name = family_name + "-" + i.capitalize()
        font_otf = otf_path + font_name + ".otf"
        font_json = json_path + font_name + ".json"
        otfcc_dump(font_otf, font_json)
        unicode_glyphs = get_unicode_info(font_json)
        non_unicode_glyphs = get_non_unicode_info(
            font_json, non_unicode_data, font_name, len(unicode_glyphs),
            show_info=False)
        cmap.append(unicode_glyphs + non_unicode_glyphs)
    return cmap

def otfcc_dump(otf_file, json_file):
    """
    Use `otfcc` library for JSON serialization.
    """
    run_process(otfcc, ["--pretty", "-o", json_file, otf_file])

def run_process(cmd, args):
    """
    Run `cmd` with `args`. Spaces will be added automatically.
    """
    cmd_line = cmd
    for i in args:
        cmd_line += (" " + i)
    os.system(cmd_line)

def get_unicode_info(json_file):
    """
    Return a list of `(<encoding dec>, <unicode dec>, <glyph index dec>, <glyph name>)`.
    `glyph name` will be `uniXXXX` or `uXXXXX`.
    """
    with open(json_file, "r") as f:
        result = json.load(f)["cmap"].keys()
    for idx, item in enumerate(result):
        d = int(item)
        item = (d, hex(d)[2:])
        result[idx] = item
    result.sort(key=lambda x: x[0]) # Now it's `(<unicode dec>, <unicode hex>)`
    for idx, item in enumerate(result):
        item = (item[0], item[0], idx, make_glyph_name(item[1]))
        result[idx] = item
    return result

def make_glyph_name(unicode_hex):
    """
    Return `uXXXXX` if `hex` >= 0x10000, `uniXXXX` if `hex` < 0x10000.
    """
    u_str = unicode_hex.upper()
    l = len(u_str)
    if l == 5:
        return "u" + u_str
    if l == 4:
        return "uni" + u_str
    if l == 3:
        return "uni0" + u_str
    if l == 2:
        return "uni00" + u_str

def get_non_unicode_info(
        json_file,
        non_unicode_data_file,
        font_name,
        unicode_glyphs_num,
        show_info=True):
    """
    Args:
        `glyphs_set`:  non-unicode glyphs from JSON
        `glyphs_list`: non-unicode glyphs from `non-unicode.txt`
        `font_name`:   name of the font
    """
    glyphs_set = get_non_unicode_from_json(json_file)
    glyphs_list = get_non_unicode_from_data(non_unicode_data_file)
    result = []
    # Check whether glyphs in `non_unicode_data_file` can be found in `json_file`.
    for i in glyphs_list:
        if i in glyphs_set:
            result.append(i)
        else:
            if show_info:
                print("Warning: Glyph \"" + i + "\" not found in " + font_name)
    # Check whether glyphs in `json_file` can be found in `non_unicode_data_file`.
    for i in glyphs_set - set(result):
        if show_info:
            print("Warning: Glyph \"" + i + "\" in " + font_name
                + "not found in \"non-unicode.txt\"")
    # Add encoding, unicode and index.
    # `-1` is the codepoint for non-unicode characters.
    for idx, item in enumerate(result):
        item = (non_unicode_begin_idx + idx, -1, unicode_glyphs_num + idx, item)
        result[idx] = item
    return result

def get_non_unicode_from_json(json_file):
    with open(json_file, "r") as f:
        json_data = json.load(f)
        glyphs_unicode = json_data["cmap"].values()
        glyphs_all = json_data["glyph_order"]
    return set(glyphs_all) - set(glyphs_unicode)

def get_non_unicode_from_data(non_unicode_data_file):
    glyphs_non_unicode = []
    with open(non_unicode_data_file, "r") as f:
        for line in f:
            s = line.strip()
            if not s.startswith(";"):
                glyphs_non_unicode.append(s)
    return glyphs_non_unicode

# Add underline
def normalize_file_name(file_name):
    return re.sub(r"^(u[^n].*)(\D)$", r"\1_\2", file_name)

#####################
# 1st dimension: weight
# 2nd dimension: sorted by index
# 3rd dimension: (<encoding dec>, <unicode dec>, <glyph index dec>, <glyph name>)
cmap = get_cmap()
#for weight_i in cmap:
    #for j in i:
    #    print(j)
    #print("+++++++++++++++++++++++++++++++++++++++++")
    #match = next(y for y in i if y[1]==32)
    #print(match)

#                       1            2   3             4     5     6
pattern = re.compile(r"(StartChar: )(.+)(\nEncoding: )(\S+) (\S+) (\S+)\n")

# #HACK
# sfd_path = "./temp/"

for idx, item in enumerate(weights):
    glyph_files = glob.glob(sfd_path + family_name_full + "-" + item + ".sfdir/" + "*.glyph")
    new_glyph_files = []
    #print(len(cmap[0]))
    #print(len(glyph_files))
    for glyph_file in glyph_files:
        with open(glyph_file, "r") as f:
            glyph_content = f.read()
        #print("===============================")
        #print(glyph_content)
        #print("*******************************")
        m = re.match(pattern, glyph_content)

        # The 2nd number in `encoding`
        unicode_idx = m.group(5)
        
        if unicode_idx != -1:
            e = next((x for x in cmap[idx] if x[1] == int(unicode_idx)), None)
            meta = m.group(1) + e[3] + \
                   m.group(3) + str(e[0]) + " " + str(e[1]) + " " + str(e[2]) + "\n"
        else:
            #TODO
            meta = m.group(0)

        new_file_name = sfd_path + family_name_full + "-" + item + ".sfdir/" + \
                        normalize_file_name(e[3]) + ".glyph"
        new_content = re.sub(pattern, meta, glyph_content)
        new_glyph_files.append((new_file_name, new_content))

    # !!!!!!!!!!!!!!!!!!!!!!!
    for glyph_file in glyph_files:
        os.remove(glyph_file)

    for new_glyph_file in new_glyph_files:
        with open(new_glyph_file[0], "w") as f:
            f.write(new_glyph_file[1])
