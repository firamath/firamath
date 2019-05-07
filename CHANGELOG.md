# Changelog of Fira Math

The format is based on [Keep a Changelog](https://keepachangelog.com).

## [Unreleased]

- Added:
  - `.notdef` for all weights
  - White and black circles, including `\cdot`, `\circ`, etc - [#34](https://github.com/firamath/firamath/issues/34)
- Changed:
  - Update to Unicode 12.0.1 (no actual changes in the font itself)
  - Remove empty placeholder glyphs
- Improved:
  - Now pre-built fonts of the latest development version can be download from [bintray](https://bintray.com/firamath/firamath/firamath-travis)

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.4-beta-3...master).

## v0.4-beta-3 (2019-02-20)

- Added:
  - Inline version of integral, summation and product symbols - [#30](https://github.com/firamath/firamath/issues/30)
  - Arrows
  - Some binary operators
- Fixed:
  - `ssty` for primes
  - Some wrong mappings - [#31](https://github.com/firamath/firamath/issues/31)
- Changed:
  - Adjust MATH constants `ScriptPercentScaleDown` and `ScriptScriptPercentScaleDown`. See [wspr/unicode-math#510](https://github.com/wspr/unicode-math/issues/510)
- Known issues:
  - ~~Uncreated arrows use empty glyph as a placeholder~~ - *fixed in v0.4-beta-4* TODO

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.4-beta-2...v0.4-beta-3).

## v0.4-beta-2 (2019-01-31)

- Added:
  - Integral, summation and product symbols (only display style) - [#21](https://github.com/firamath/firamath/issues/21)
- Fixed:
  - Correct Mathematical Capital Theta Symbols (`\varTheta`)
- Improved:
  - MATH-relevant data are moved to a single JSON file
  - `autoHint`, `removeOverlap` and `round` will be done when generating OTF files
  - Check fonts in ci

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.4-beta-1...v0.4-beta-2).

## v0.4-beta-1 (2018-12-22)

- Added:
  - Support multiple weights - [#1](https://github.com/firamath/firamath/issues/1), [#4](https://github.com/firamath/firamath/issues/4) and [#9](https://github.com/firamath/firamath/issues/9)
- Changed:
  - Use single `.sfd` files instead of the `.sfdir` folders
  - Latin, Greek and Cyrillic characters now (almost) follow Adobe Latin-3, Greek-1 and Cyrillic-1 charcter sets
- Improved:
  - Optimize the glyph of integrals, primes, etc
  - Python scripts are re-written with FontForge's API
- Known issues:
  - Only few of the basic glyphs have been created
  - ~~Interpolated points are not rounded to integer, and overlapped paths are not removed~~ - *fixed in v0.4-beta-2*
  - Now the metrics are just from the original FiraGO/FiraSans, but should be modified for math
  - ~~For primes, `ssty2` is identical to `ssty1`. See [wspr/unicode-math#503](https://github.com/wspr/unicode-math/issues/503)~~ - *fixed in v0.4-beta-3*
  - ~~Mathematical Capital Theta Symbols are not correct~~ - *fixed in v0.4-beta-2*
  - This version is highly experimental so I will not upload to CTAN

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.3.1...v0.4-beta-1).

## v0.3.1 (2018-10-26)

- Changed:
  - Update to Unicode 11.0
  - Update `name` table
  - Migrate to [firamath/firamath](https://github.com/firamath/firamath)
- Fixed:
  - Super-/subscripts position of large delimiters - [#16](https://github.com/firamath/firamath/issues/16)
- Improved:
  - Continuous integration uses Ubuntu 18.04 Bionic and FontForge 20170924 now
  - Source files are renamed as PostScript names, i.e. `FiraMath-<Weight>`
  - Do not depend on `otfcc` library

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.3...v0.3.1).

## v0.3 (2018-09-15)

- Added:
  - Mathematical double-struck (blackboard) letters
  - More large delimiters and radicals
  - Some relation symbols (`\colon` etc) - [#15](https://github.com/firamath/firamath/issues/15)
- Changed:
  - Default digits become mono-spaced (and slightly modified, according to FiraGO), while the proportional digits are now under `pnum` tag - [#10](https://github.com/firamath/firamath/issues/10)
  - Integral contours are removed
- Improved:
  - Extensible delimiters are re-designed
  - Now Fira Math is available on CTAN (named as [`firamath`](https://ctan.org/pkg/firamath)) - [#3](https://github.com/firamath/firamath/issues/3)
  - Use [continuous integration](https://travis-ci.org/firamath/firamath) (CI) for basic building test

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.2.2...v0.3).

## v0.2.2 (2018-06-28)

- Added:
  - Large variants of `\cuberoot` and `\fourthroot`
  - More top/bottom accents
- Fixed:
  - Position of radical degree - [#8](https://github.com/firamath/firamath/issues/8)
- Improved:
  - Use feature files for OpenType feature specifications
  - Update [README](README.md) for LaTeX and Microsoft Word usage - [#7](https://github.com/firamath/firamath/pull/7). Thanks [@bwiernik](https://github.com/bwiernik)!
  - Add [CHANGELOG](CHANGELOG.md)

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.2.1...v0.2.2).

## v0.2.1 (2018-06-25)

- Fixed:
  - Wrong intersection behavior in `\oint`, etc - [#6](https://github.com/firamath/firamath/issues/6)

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.2...v0.2.1).

## v0.2 (2018-06-23)

- Added:
  - Latin supplement and extended
  - More math operators and relation symbols
  - More arrows (redesigned)
  - Stylistic sets:
    - `ss01`: Upright Integrals
    - `ss02`: Planck Constant with Bar
    - `ss03`: Complement Alternates
- Changed:
  - Font name has been changed to `FiraMath-Regular.otf` for multi-weight support in the near future.
- Fixed:
  - Wrong mapping of Greek letters - [#5](https://github.com/firamath/firamath/issues/5)

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/v0.1...v0.2).

## v0.1 (2018-01-20)

- Latin and Greek letters with different styles
- Basic binary relation symbols
- Fraction and radical
- Delimeters
- Huge operators (e.g. integral and summation)
- Math accents
- Over-/underline and over-/underbraces

More details can be found in the [GitHub commit log](https://github.com/firamath/firamath/compare/5011a1e9...v0.1).
