@echo off

fontforge -script "scripts/generate.pe" fira-math.sfdir
move *.otf otf

cd test
xelatex font-test.tex
cd ..
