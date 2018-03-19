@echo off

xelatex --interaction=batchmode 1
rem xelatex --interaction=batchmode 2
rem xelatex --interaction=batchmode 3

".\pdf2svg-windows\dist-64bits\pdf2svg.exe" "1.pdf" "1.svg"
rem ".\pdf2svg-windows\dist-64bits\pdf2svg.exe" "2.pdf" "2.svg"

move "1.svg" "..\..\images\fourier.svg"

del *.aux *.log
