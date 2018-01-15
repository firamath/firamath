@echo off

fontforge -script "scripts/generate.pe" fira-math.sfdir
move *.otf  assets/
move *.woff assets/

cd test
xelatex font-test.tex
cd ..
