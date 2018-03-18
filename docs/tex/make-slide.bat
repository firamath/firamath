@echo off

xelatex slide.tex
E:\Files\TeX\my-projects\fduthesis\tools\convert -density 200 "slide.pdf" "slide.png"

move *.png ..\images\
