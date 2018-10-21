(* ::Package:: *)

Remove["Global`*"]


(* ::Section:: *)
(*Functions*)


getSpline[glyphData_] :=
  Module[{rawSplineSet, splineSet},
    rawSplineSet = First @
      StringCases[glyphData, "SplineSet\n" ~~ x__ ~~ "\nEndSplineSet" -> x];
    splineSet = Partition[#, 2] & @ Prepend[#, ""] & @
      StringSplit[rawSplineSet, "\n" ~~ x: WordCharacter -> x];
    StringSplit[StringJoin /@ splineSet, "\n "]
  ]


getCurve[strList_] :=
  $getCurve @@@ Partition[StringSplit @ strList, 2, 1]
$getCurve[p1_, p2_] :=
  Module[{$p1 = ToExpression @ p1[[;;-3]], $p2 = ToExpression @ p2[[;;-3]]},
    If[p2[[-2]] == "c",
      (* c: curve to *)
      <|
        "Curves"      -> BezierCurve @
          { $p1[[{-2, -1}]], $p2[[{1, 2}]],   $p2[[{3, 4}]], $p2[[{5, 6}]]},
        "Ctrl.Lines"  -> Line @
          {{$p1[[{-2, -1}]], $p2[[{1, 2}]]}, {$p2[[{3, 4}]], $p2[[{5, 6}]]}},
        "Points"      -> Point @ {$p1[[{-2, -1}]], $p2[[{5, 6}]]},
        "Ctrl.Points" -> Point @ {$p2[[{ 1,  2}]], $p2[[{3, 4}]]}
      |>,
      (* l: line to *)
      <|
        "Curves" -> Line  @ {$p1[[{-2, -1}]], $p2[[{1, 2}]]},
        "Points" -> Point @ {$p1[[{-2, -1}]], $p2[[{1, 2}]]}
      |>
    ]
  ]


interpolate[c1_, c2_, t_] :=
  Head[c1] @ ((1 - t) #[[1]] + t #[[2]]) & @ Level[{c1, c2}, {2}]
SetAttributes[interpolate, Listable]


color1 = Gray;
color2 = RGBColor[0.461492, 0.563303, 0.0104797];
color3 = RGBColor[0.65, 0., 0.];
color4 = RGBColor[0.0504678, 0.526626, 0.627561];
plotCurve[curveList_, opts: OptionsPattern[]] :=
  Graphics[
    {
      color1, Thickness @ 0.005, Map[Lookup[#, "Curves",      {}] &, curveList, {2}],
      color2, Thickness @ 0.003, Map[Lookup[#, "Ctrl.Lines",  {}] &, curveList, {2}],
      color3, PointSize @ 0.01,  Map[Lookup[#, "Points",      {}] &, curveList, {2}],
      color4, PointSize @ 0.01,  Map[Lookup[#, "Ctrl.Points", {}] &, curveList, {2}]
    },
    FilterRules[{opts}, Options @ Graphics]
  ]


plotGlyph[file_, opts: OptionsPattern[]] :=
  plotCurve[getCurve /@ getSpline @ Import @ file,
    FilterRules[{opts}, Options @ Graphics]]


plotInterpolatedGlyphs[file1_, file2_, opts: OptionsPattern[]] :=
  DynamicModule[{c1, c2},
    c1 = getCurve /@ getSpline @ Import @ file1;
    c2 = getCurve /@ getSpline @ Import @ file2;
    Manipulate[plotCurve[interpolate[c1, c2, t], FilterRules[{opts}, Options @ Graphics]],
      {t, OptionValue["range"][[1]], OptionValue["range"][[2]]}]
  ]
Options[plotInterpolatedGlyphs] = Append[Options @ Graphics, "range" -> {0, 1}];


(* ::Section:: *)
(*Plot*)


SetDirectory[NotebookDirectory[]];
$path = FileNameJoin[{ParentDirectory[], "src"}];


{plotGlyph[FileNameJoin[{$path, "FiraMath-Thin.sfdir", "uni0123.glyph"}],
  Frame -> True, ImageSize -> 200],
 plotGlyph[FileNameJoin[{$path, "FiraMath-Bold.sfdir", "uni0123.glyph"}],
  Frame -> True, ImageSize -> 200]}


$name = "uni0123";
$range = {{-50, 600}, {-250, 850}};
$aspectRatio = 1 / Divide @@ Subtract @@ Transpose @ $range;
plotInterpolatedGlyphs[
  FileNameJoin[{$path, "FiraMath-Thin.sfdir", $name <> ".glyph"}],
  FileNameJoin[{$path, "FiraMath-Bold.sfdir", $name <> ".glyph"}],
  PlotRange -> $range,
  Frame -> True, GridLines -> {None, {{0, Dashed}}},
  AspectRatio -> $aspectRatio, ImageSize -> 300]
Remove[$name, $range, $aspectRatio];
