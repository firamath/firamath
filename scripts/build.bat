@echo off

if "%1"=="font"  goto FONT
if "%1"=="doc"   goto DOCS
if "%1"=="slide" goto SLIDE
if "%1"=="all"   goto MAKEALL
if "%1"=="clean" goto CLEAN
goto TEST

:FONT
    fontforge -script "scripts\generate.pe" "fira-math.sfdir"
    move *.otf  "docs\assets\"
    move *.woff "docs\assets\"
goto :EOF

:TEST
    call :FONT
    cd "test\"
    xelatex "font-test.tex"
    cd ..
goto :EOF

:DOCS
    cd "docs\tex\"
    latexmk -g -xelatex "specimen.tex"
    latexmk -g -xelatex "unimath-symbols.tex"
    cd ..\..
goto :EOF

:SLIDE
    cd "docs\tex\"
    "..\..\tools\convert.exe" -density 200 "slide.pdf" "slide.png"
    move "slide.png" "..\images"
    cd ..\..
goto :EOF

:DOCS_ALL
    call :FONT
    call :DOCS
    call :SLIDE
goto :EOF

:CLEAN_AUX
    del *.aux
    del *.fdb_latexmk
    del *.fls
    del *.log
    del *.nav
    del *.out
    del *.snm
    del *.toc
    del *.xdv
goto :EOF

:CLEAN
    cd "test\"
    call :CLEAN_AUX
    cd "..\docs\tex"
    call :CLEAN_AUX
    cd ..\..
goto :EOF
