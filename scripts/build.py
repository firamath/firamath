#!/usr/bin/python
"""Build script for Fira Math. It can

- Generate fonts with FontForge.
- Run tests with XeLaTeX.
- Generate documentations.
"""

from __future__ import print_function

import argparse
import datetime
import os
import platform

import fontforge as ff

# Even on Windows, we should use `/` for paths, otherwise font generation will raise an error.
PWD              = os.getcwd()
SFD_PATH         = PWD + "/src"
FEATURE_PATH     = PWD + "/src/features"
OTF_PATH         = PWD + "/release/fonts"
TEST_PATH        = PWD + "/test"
DOCS_PATH        = PWD + "/docs"
# SFD_PATH         = os.path.join(PWD, "src")
# FEATURE_PATH     = os.path.join(PWD, "src", "features")
# OTF_PATH         = os.path.join(PWD, "release", "fonts")
# TEST_PATH        = os.path.join(PWD, "test")
# DOCS_PATH        = os.path.join(PWD, "docs")
FAMILY_NAME      = "FiraMath"
TEST_FILE_NAME   = "basic"
TEST_FILE_NAME   = "weights"
DOCS_FILE_NAMES  = ["firamath-demo", "firamath-specimen", "unimath-symbols"]
WEIGHT_LIST      = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
                    "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]
# WEIGHT_LIST      = ["Thin", "Ultra"]
# WEIGHT_LIST      = ["Regular"]


if not os.path.exists(OTF_PATH):
    os.mkdir(OTF_PATH)

def generate_fonts():
    print("FontForge version: " + ff.version())
    print("Python version: "+ platform.python_version())
    print("Platform: " + platform.platform() + "\n")
    for weight in WEIGHT_LIST:
        font_name      = FAMILY_NAME + "-" + weight
        sfd_file       = SFD_PATH + "/" + font_name + ".sfd"
        feature_file   = FEATURE_PATH + "/" + font_name + ".fea"
        otf_file       = OTF_PATH + "/" + font_name + ".otf"
        # font_name    = FAMILY_NAME + "-" + weight
        # sfd_file     = os.path.join(SFD_PATH, font_name + ".sfd")
        # feature_file = os.path.join(FEATURE_PATH, font_name + ".fea")
        # otf_file     = os.path.join(OTF_PATH, font_name + ".otf")

        font = ff.open(sfd_file)
        font.mergeFeature(feature_file)
        font.generate(otf_file, flags=("opentype", "round"))
        font.close()
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')
              + " '" + font_name + "' " + "generated.")

def check_fonts():
    for weight in WEIGHT_LIST:
        font_name = FAMILY_NAME + "-" + weight
        otf_file  = os.path.join(OTF_PATH, font_name + ".otf")
        print("\n", font_name)
        if os.path.isfile(otf_file):
            font = ff.open(otf_file)
        else:
            raise IOError("'" + font_name + ".otf' not found!")
        _check_name(font, font_name)
        _check_gsub_lookups(font)
        _check_math_table(font)
        _validate(font)
    print("\n\nAll tests passed.")

def _check_name(font, font_name):
    sfnt_font_name = font.sfnt_names[6][2]  # PostScript name
    if sfnt_font_name != font_name:
        raise ValueError("'" + font_name + "' has an incorrect name '" + sfnt_font_name + "'!")
    else:
        print("\tName check passed.")

def _check_gsub_lookups(font):
    lookups = font.gsub_lookups
    if lookups != ():
        print("\tGSUB lookups:")
        for i in lookups:
            print("\t\t", i)
    else:
        raise ValueError("'" + font.font_name + "' has empty GSUB lookups!")

def _check_math_table(font):
    if not font.math.exists():
        raise ValueError("'" + font.font_name + "' has empty MATH table!")
    else:
        print("\tMATH table check passed.")

def _validate(font):
    validation_state_dict = {glyph: font[glyph].validation_state for glyph in font}
    if sum(validation_state_dict.values()) != 0:
        print("\tGlyph validation state:")
        for glyph, state in validation_state_dict.items():
            if state != 0:
                print("\t\t" + glyph + ": " + hex(state))
    else:
        print("\tValidation passed.")

def xelatex_test():
    os.chdir(TEST_PATH)
    run_xelatex(TEST_FILE_NAME)

def run_xelatex(file_name):
    os.system("xelatex " + file_name + ".tex")

def make_docs():
    os.chdir(DOCS_PATH)
    for i in DOCS_FILE_NAMES:
        run_latexmk(i)

def run_latexmk(file_name):
    os.system("latexmk -g -xelatex " + file_name + ".tex")

def clean():
    os.chdir(TEST_PATH)
    clean_aux_files()
    os.chdir(DOCS_PATH)
    clean_aux_files()
    os.chdir(SFD_PATH)
    rm("*.bak")

def clean_aux_files():
    aux_file_suffixes = ["aux", "fdb_latexmk", "fls", "log", "nav", "out", "snm", "toc", "xdv"]
    for i in aux_file_suffixes:
        rm("*." + i)

def rm(file_name):
    if platform.system() == "Linux":
        os.system("rm -f " + file_name)
    elif platform.system() == "Windows":
        os.system("DEL /Q " + file_name)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--fonts", action="store_true", help="generate fonts")
group.add_argument("-k", "--check", action="store_true", help="check font features")
group.add_argument("-t", "--test",  action="store_true", help="run xelatex test")
group.add_argument("-d", "--docs",  action="store_true", help="generate documentations")
group.add_argument("-r", "--run",   action="store_true", help="generate fonts and run test")
group.add_argument("-a", "--all",   action="store_true", help="generate fonts and documentations")
group.add_argument("-c", "--clean", action="store_true", help="clean working directory")
args = parser.parse_args()

if args.fonts:
    generate_fonts()
if args.check:
    check_fonts()
if args.test:
    xelatex_test()
if args.docs:
    make_docs()
if args.run:
    generate_fonts()
    xelatex_test()
if args.all:
    generate_fonts()
    make_docs()
if args.clean:
    clean()
