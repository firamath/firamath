# Fira Math

[![Build Status](https://travis-ci.org/Stone-Zeng/FiraMath.svg?branch=master)](https://travis-ci.org/Stone-Zeng/FiraMath)
[![CTAN](https://img.shields.io/ctan/v/firamath.svg)](https://www.ctan.org/pkg/firamath)
[![GitHub release](https://img.shields.io/github/release/Stone-Zeng/FiraMath/all.svg)](https://github.com/Stone-Zeng/FiraMath/releases/latest)

Fira Math is a sans-serif font with Unicode math support. This font is a fork of

- [FiraSans](https://github.com/bBoxType/FiraSans)
- [FiraGO](https://github.com/bBoxType/FiraGO)

## Usage

Fira Math can be used in LaTeX or Microsoft Word after installed on your OS.

### LaTeX

```latex
% Compiled with XeLaTeX or LuaLaTeX
\documentclass{article}
\usepackage{amsmath}
\usepackage[mathrm=sym]{unicode-math}
\setmathfont{Fira Math}

\begin{document}
\[
  \int_0^{\mathrm{\pi}} \sin x \, \mathrm{d}x = 2
\]
\end{document}
```

You may try the [`firamath-otf`](https://ctan.org/pkg/firamath-otf) package as well. - Thanks [Herbert Voß](https://github.com/hvoss49)!

### Microsoft Word

1. Create a new equation. Then select the little *additional settings* corner.

1. In the menu, change the *Default font* to Fira Math.

1. In order for the changes to take effect, you will have to create a new equation environment (the current one will not be changed).

1. To change the font in existing equations, select the equation text and select an OpenType math-enabled font (such as Fira Math).

See <https://superuser.com/q/1114697>.

## Showcase

![Showcase](https://raw.githubusercontent.com/Stone-Zeng/FiraMath/master/docs/images/slide.png)

## Contributing

[Issues](https://github.com/Stone-Zeng/FiraMath/issues) and
[pull requests](https://github.com/Stone-Zeng/FiraMath/pulls)
are always welcome.

## License

This Font Software is licensed under the [SIL Open Font License](http://scripts.sil.org/OFL), Version 1.1.

-----

Copyright (C) 2018 by Xiangdong Zeng.
