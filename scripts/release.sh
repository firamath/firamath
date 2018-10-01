#!/usr/bin/env sh

# This script is used for creating CTAN archive of firamath.

# On CTAN, the package name is `firamath`, rather than `fira-math`
# or `FiraMath`.
JOB_NAME=firamath
WORKING_DIR=$PWD
RELEASE_DIR=$WORKING_DIR/release

mkdir -p $RELEASE_DIR

# Copy all the files to system temp folder, in order to use
# chmod correctly.
TEMP_DIR=/tmp/$JOB_NAME
TDS_DIR=$TEMP_DIR/TDS
CTAN_DIR=$TEMP_DIR/$JOB_NAME
FONT_DIR=$TDS_DIR/fonts/opentype/public/$JOB_NAME
DOC_DIR=$TDS_DIR/doc/fonts/$JOB_NAME

mkdir -p $TEMP_DIR
mkdir -p $TDS_DIR
mkdir -p $CTAN_DIR
mkdir -p $FONT_DIR
mkdir -p $DOC_DIR

# TODO: we only need `Regular` weight now
cp $WORKING_DIR/release/fonts/FiraMath-Regular.otf  $TEMP_DIR
cp $WORKING_DIR/tex/README.md                       $TEMP_DIR
cp $WORKING_DIR/tex/firamath-demo.tex               $TEMP_DIR
cp $WORKING_DIR/tex/firamath-specimen.tex           $TEMP_DIR
cp $WORKING_DIR/tex/firamath-demo.pdf               $TEMP_DIR
cp $WORKING_DIR/tex/firamath-specimen.pdf           $TEMP_DIR
cp $WORKING_DIR/data/firamath-non-unicode.txt       $TEMP_DIR

cd $TEMP_DIR

# Replace local settings in TeX files
# See ...
PATTERN=":a;N;s/%%<DEBUG>\n\(.*\)\n%%<RELEASE>\n%%\(.*\)\n%%<END>/\2/g;ba"

sed -i $PATTERN firamath-demo.tex
sed -i $PATTERN firamath-specimen.tex

# All files should be rw-r--r--
chmod 644 $TEMP_DIR/*.*

cp $TEMP_DIR/*.otf $FONT_DIR
cp $TEMP_DIR/*.md  $DOC_DIR
cp $TEMP_DIR/*.pdf $DOC_DIR
cp $TEMP_DIR/*.tex $DOC_DIR
cp $TEMP_DIR/*.txt $DOC_DIR

# Make TDS zip
cd $TDS_DIR
zip -q -r -9 $JOB_NAME.tds.zip .

cp $TEMP_DIR/*.otf $CTAN_DIR
cp $TEMP_DIR/*.md  $CTAN_DIR
cp $TEMP_DIR/*.pdf $CTAN_DIR
cp $TEMP_DIR/*.tex $CTAN_DIR
cp $TEMP_DIR/*.txt $CTAN_DIR

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
