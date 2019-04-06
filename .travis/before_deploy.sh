#!/usr/bin/env sh

BUILD_DATE=$(date "+%Y-%m-%d")
BUILD_SUFFIX=$BUILD_DATE-$(echo $TRAVIS_COMMIT | cut -c1-7)
BINTRAY_DESCRIPTOR=$TRAVIS_BUILD_DIR/.travis/bintray_descriptor.json

zip -j ./release/firamath-otf-$BUILD_SUFFIX.zip ./release/fonts/*.otf

sed -i "s/<CI-XXXX>/ci-$BUILD_DATE/g" $BINTRAY_DESCRIPTOR   || true
sed -i "s/<RELEASE-XXXX>/$BUILD_DATE/g" $BINTRAY_DESCRIPTOR || true

echo "Bintray descriptor:"
cat $BINTRAY_DESCRIPTOR
