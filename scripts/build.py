#!/usr/bin/python

import argparse
import datetime
import os
import platform

import fontforge

pwd              = os.getcwd()
sfd_path         = pwd + "/src/"
feature_path     = pwd + "/src/features/"
otf_path         = pwd + "/docs/assets/"
test_path        = pwd + "/test/"
docs_path        = pwd + "/docs/tex/"
family_name      = "FiraMath"
family_name_full = "fira-math"
test_file_name   = "font-test"
docs_file_names  = ["specimen", "unimath-symbols"]
weights          = ["thin", "light", "regular", "medium", "bold"]
# weights          = ["regular"]

def generate_fonts():
    print("FontForge version: " + fontforge.version())
    print("Python version: "+ platform.python_version())
    print("Platform: " + platform.platform() + "\n")
    for i in weights:
        font_name = family_name + "-" + i.capitalize()
        font_name_full = family_name_full + "-" + i
        font = fontforge.open(sfd_path + font_name_full + ".sfdir")
        font.mergeFeature(feature_path + font_name_full + ".fea")
        font.generate(otf_path + font_name + ".otf", flags=("opentype"))
        print(datetime.datetime.now().strftime('[%Y-%m-%d %H:%M:%S.%f]')
            + " '" + font_name + "' " + "generated successfully.")

def xelatex_test():
    os.chdir(test_path)
    run_xelatex(test_file_name)

def run_xelatex(file_name):
    os.system("xelatex " + file_name + ".tex")

def make_docs():
    os.chdir(docs_path)
    for i in docs_file_names:
        run_latexmk(i)

def run_latexmk(file_name):
    os.system("latexmk -g -xelatex " + file_name + ".tex")

def clean():
    os.chdir(test_path)
    clean_aux_files()
    os.chdir(docs_path)
    clean_aux_files()

def clean_aux_files():
    aux_file_suffixes = ["aux", "fdb_latexmk", "fls", "log", "nav", "out", "snm", "toc", "xdv"]
    for i in aux_file_suffixes:
        os.system("rm -f *." + i)

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-f", "--fonts", action="store_true", help="generate fonts")
group.add_argument("-t", "--test",  action="store_true", help="run xelatex test")
group.add_argument("-d", "--docs",  action="store_true", help="generate documentations")
group.add_argument("-r", "--run",   action="store_true", help="generate fonts and run test")
group.add_argument("-a", "--all",   action="store_true", help="generate fonts and documentations")
group.add_argument("-c", "--clean", action="store_true", help="clean working directory")
args = parser.parse_args()

if args.fonts:
    generate_fonts()
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
