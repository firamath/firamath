#!/usr/bin/env sh

# This script is used for creating CTAN archive of firamath.

# On CTAN, the package name is `firamath`, rather than `fira-math`
# or `FiraMath`.
JOB_NAME=firamath

# Use LuaTeX as Lua interpreter.
LUA=texlua

WORKING_DIR=$PWD
RELEASE_DIR=$WORKING_DIR/release
TEMP_DIR=$WORKING_DIR/temp/release
TDS_DIR=$TEMP_DIR/TDS
CTAN_DIR=$TEMP_DIR/$JOB_NAME
FONT_DIR=$TDS_DIR/fonts/opentype/public/$JOB_NAME
DOC_DIR=$TDS_DIR/doc/fonts/$JOB_NAME

mkdir -p $RELEASE_DIR
mkdir -p $TEMP_DIR
mkdir -p $TDS_DIR
mkdir -p $CTAN_DIR
mkdir -p $FONT_DIR
mkdir -p $DOC_DIR

cp $WORKING_DIR/release/fonts/FiraMath-Regular.otf $TEMP_DIR
cp $WORKING_DIR/docs/firamath-demo.tex         $TEMP_DIR
cp $WORKING_DIR/docs/firamath-specimen.tex     $TEMP_DIR
cp $WORKING_DIR/docs/firamath-glyph-list.tex   $TEMP_DIR
cp $WORKING_DIR/docs/firamath-demo.pdf         $TEMP_DIR
cp $WORKING_DIR/docs/firamath-specimen.pdf     $TEMP_DIR

cp $WORKING_DIR/docs/README.ctan.md            $TEMP_DIR/README.md

cd $TEMP_DIR

# Replace local settings in TeX files
echo "file = io.open(arg[1], 'r')
str = string.gsub(file:read('*a'),
    '%%%%<DEBUG>.*%%%%<RELEASE>\\\\n(.*)%%%%<END>\\\\n',
    function (s) return string.gsub(s, '%%%%', '') end)
file:close()
file = io.open(arg[1], 'w')
file:write(str)
file:close()
" > _replace.lua
$LUA _replace.lua firamath-demo.tex
$LUA _replace.lua firamath-specimen.tex

# All files should be rw-r--r--
chmod 644 $TEMP_DIR/*.*

cp $TEMP_DIR/*.otf $FONT_DIR
cp $TEMP_DIR/*.md  $DOC_DIR
cp $TEMP_DIR/*.pdf $DOC_DIR
cp $TEMP_DIR/*.tex $DOC_DIR

# Make TDS zip
cd $TDS_DIR
zip -q -r -9 $JOB_NAME.tds.zip .

cp $TEMP_DIR/*.otf $CTAN_DIR
cp $TEMP_DIR/*.md  $CTAN_DIR
cp $TEMP_DIR/*.pdf $CTAN_DIR
cp $TEMP_DIR/*.tex $CTAN_DIR

rm $TEMP_DIR/*.*
cp $TDS_DIR/*.zip $TEMP_DIR
rm -r $TDS_DIR

# Make CTAN zip
cd $TEMP_DIR
zip -q -r -9 $JOB_NAME.zip .

cd $WORKING_DIR
cp -f $TEMP_DIR/$JOB_NAME.zip     $RELEASE_DIR
cp -f $TEMP_DIR/$JOB_NAME.tds.zip $RELEASE_DIR

rm -r $TEMP_DIR
