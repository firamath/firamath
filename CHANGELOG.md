# Changelog of Fira Math

The format is based on [Keep a Changelog](https://keepachangelog.com),

## [Unreleased]

- Changed:
  - Update to Unicode 11.0
  - Update `name` table
- Fixed:
  - Super-/subscripts position of large delimiters - [#16](https://github.com/Stone-Zeng/FiraMath/issues/16)
- Improved:
  - Continuous integration uses Ubuntu 18.04 Bionic and FontForge 20170924 now
  - Source files are renamed as PostScript names, i.e. `FiraMath-<Weight>`
  - Do not depend on `otfcc` library

## v0.3 (2018-09-15)

- Added:
  - Mathematical double-struck (blackboard) letters
  - More large delimiters and radicals
  - Some relation symbols (`\colon` etc) - [#15](https://github.com/Stone-Zeng/FiraMath/issues/15)
- Changed:
  - Default digits become mono-spaced (and slightly modified, according to FiraGO), while the proportional digits are now under `pnum` tag - [#10](https://github.com/Stone-Zeng/FiraMath/issues/10)
  - Integral contours are removed
- Improved:
  - Extensible delimiters are re-designed
  - Now Fira Math is available on CTAN (named as [`firamath`](https://ctan.org/pkg/firamath)) - [#3](https://github.com/Stone-Zeng/FiraMath/issues/3)
  - Use [continuous integration](https://travis-ci.org/Stone-Zeng/FiraMath) (CI) for basic building test

## v0.2.2 (2018-06-28)

- Added:
  - Large variants of `\cuberoot` and `\fourthroot`
  - More top/bottom accents
- Fixed:
  - Position of radical degree - [#8](https://github.com/Stone-Zeng/FiraMath/issues/8)
- Improved:
  - Use feature files for OpenType feature specifications
  - Update [README](README.md) for LaTeX and Microsoft Word usage - [#7](https://github.com/Stone-Zeng/FiraMath/pull/7). Thanks [@bwiernik](https://github.com/bwiernik)!
  - Add [CHANGELOG](CHANGELOG.md)

## v0.2.1 (2018-06-25)

- Fixed:
  - Wrong intersection behavior in `\oint`, etc - [#6](https://github.com/Stone-Zeng/FiraMath/issues/6)

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
  - Wrong mapping of Greek letters - [#5](https://github.com/Stone-Zeng/FiraMath/issues/5)

## v0.1 (2018-01-20)

- Latin and Greek letters with different styles
- Basic binary relation symbols
- Fraction and radical
- Delimeters
- Huge operators (e.g. integral and summation)
- Math accents
- Over-/underline and over-/underbraces
