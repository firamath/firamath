#!/usr/bin/env sh

# NOT FINISHED!

fontforge -script "scripts/generate.pe" "../fira-math.sfdir"
move *.otf  "docs/assets/"
move *.woff "docs/assets/"

cd "test"
xelatex "font-test.tex"
cd ..
