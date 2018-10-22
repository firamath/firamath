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
  plotCurve[getCurve /@ getSpline @ ReadString @ file,
    FilterRules[{opts}, Options @ Graphics]]


plotInterpolatedGlyphs[file1_, file2_, opts: OptionsPattern[]] :=
  DynamicModule[{c1, c2},
    {c1, c2} = (getCurve /@ getSpline @ ReadString @ #) & /@ {file1, file2};
    c1 = getCurve /@ getSpline @ ReadString @ file1;
    c2 = getCurve /@ getSpline @ ReadString @ file2;
    Manipulate[
      plotCurve[interpolate[c1, c2, t], FilterRules[{opts}, Options @ Graphics]],
      {t, OptionValue["range"][[1]], OptionValue["range"][[2]]}]
  ]
plotInterpolatedGlyphs[file1_, file2_, file0_, opts: OptionsPattern[]] :=
  DynamicModule[{c1, c2, c0},
    {c1, c2, c0} = (getCurve /@ getSpline @ ReadString @ #) & /@ {file1, file2, file0};
    (*c1 = getCurve /@ getSpline @ ReadString @ file1;
    c2 = getCurve /@ getSpline @ ReadString @ file2;
    c0 = getCurve /@ getSpline @ ReadString @ file0;*)
    Manipulate[
      plotCurve[Append[interpolate[c1, c2, t], c0], FilterRules[{opts}, Options @ Graphics]],
      {t, OptionValue["range"][[1]], OptionValue["range"][[2]]}]
  ]
Options[plotInterpolatedGlyphs] = Append[Options @ Graphics, "range" -> {0, 1}];


getRawPoints[strList_] :=
  Flatten[#[[;;-3]] & /@ StringSplit[strList]]
glyphDistance[file1_, file2_] :=
  Module[{p1, p2},
    p1 = Flatten[getRawPoints /@ getSpline @ ReadString @ file1];
    p2 = Flatten[getRawPoints /@ getSpline @ ReadString @ file2];
    EuclideanDistance @@@
      Transpose[ToExpression @ Partition[#, 2] & /@ {p1, p2}] // Mean
  ]
glyphInterpolationDistance[file1_, file2_, t_, file0_] :=
  Module[{p1, p2, p0, pInt},
    {p1, p2, p0} =
      ToExpression @ Flatten[getRawPoints /@ getSpline @ ReadString @ #] & /@ {file1, file2, file0};
    pInt = ((1 - t) #1 + t #2) & @@@ Transpose @ {p1, p2};
    EuclideanDistance @@@
      Transpose[ToExpression @ Partition[#, 2] & /@ {p0, pInt}] // Mean
  ]


(* ::Section:: *)
(*Plot*)


SetDirectory[NotebookDirectory[]];
$path = FileNameJoin[{ParentDirectory[], "src"}];


{plotGlyph[FileNameJoin[{$path, "FiraMath-Thin.sfdir", "uni0123.glyph"}],
  Frame -> True, ImageSize -> 200],
 plotGlyph[FileNameJoin[{$path, "FiraMath-Bold.sfdir", "uni0123.glyph"}],
  Frame -> True, ImageSize -> 200]}


$name = "uni0031";
$range = {{-50, 700}, {-50, 850}};
$aspectRatio = 1 / Divide @@ Subtract @@ Transpose @ $range;
plotInterpolatedGlyphs[
  FileNameJoin[{$path, "FiraMath-Thin.sfdir", $name <> ".glyph"}],
  FileNameJoin[{$path, "FiraMath-Bold.sfdir", $name <> ".glyph"}],
  FileNameJoin[{$path, "FiraMath-Regular.sfdir", $name <> ".glyph"}],
  PlotRange -> $range,
  Frame -> True, GridLines -> {None, {{0, Dashed}}},
  AspectRatio -> $aspectRatio, ImageSize -> 500]
Remove[$name, $range, $aspectRatio];


(* ::Section:: *)
(*Optimize*)


Through[{Mean, StandardDeviation}[#]]& /@
  {
    {0.275, 0.300, 0.270, 0.284, 0.290, 0.280, 0.290},
    {0.508, 0.566, 0.518, 0.544, 0.560, 0.560, 0.550},
    {0.792, 0.792, 0.788, 0.792, 0.798, 0.782, 0.788}
  }


N@glyphDistance[
  FileNameJoin[{$path, "FiraMath-Thin.sfdir", "uni0041.glyph"}],
  FileNameJoin[{$path, "FiraMath-Bold.sfdir", "uni0041.glyph"}]]


N@glyphInterpolationDistance[
  FileNameJoin[{$path, "FiraMath-Thin.sfdir", "uni0041.glyph"}],
  FileNameJoin[{$path, "FiraMath-Bold.sfdir", "uni0041.glyph"}],
  0.2,
  FileNameJoin[{$path, "FiraMath-Thin.sfdir", "uni0041.glyph"}]]


IntegerString[Range[#1] + FromDigits[#2, 16], 16] & @@@
  {{8, "31"}, {16, "40"}, {16, "60"}} // Flatten;
Echo @ Length[glyphSet = "uni00" <> ToUpperCase[#] <> ".glyph" & /@ %];
Echo @ Length[interpolateRange = Range[0.75, 0.85, 0.001]];


$fileName[weight_, glyph_] :=
  FileNameJoin[{$path, "FiraMath-" <> weight <> ".sfdir", glyph}]
$findInterpolationArg[weight_, glyphSet_, interpolateRange_] :=
  AssociationThread[interpolateRange -> Transpose @
    ParallelTable[
      N @ glyphInterpolationDistance[
        $fileName["Thin", g], $fileName["Bold", g],
        t,
        $fileName[weight, g]],
      {g, glyphSet}, {t, interpolateRange}]]


$weights = {"Thin", "Light", "Regular", "Medium", "Bold"};
$weights = {"Medium"};
AbsoluteTiming[$result =
  $findInterpolationArg[#, glyphSet, interpolateRange] & /@ $weights;]


$style = With[{w = Length @ $weights, c = ColorData[97]},
  Flatten[{c[#], None, None} & /@ Range[w], 1]];
$filling = With[{w = Length @ $weights, c = ColorData[97]},
  3# - 1 -> {3#} & /@ Range[w]];
$fillingStyle = Directive[Opacity[0.1], ColorData[97][2]];
$legends = Flatten[{#, None, None} & /@ $weights];


TakeSmallest[Mean /@ #, 1] & /@ $result
Map[{Mean[#], StandardDeviation[#]} &, $result, {2}];
Normal[%] /. (x_ -> {y_, dy_}) -> {{x, y}, {x, y - dy}, {x, y + dy}};
ListPlot[Flatten[Transpose[%, 2 <-> 3], 1],
  Joined -> True, PlotStyle -> $style, Frame -> True,
  Filling -> $filling, FillingStyle -> $fillingStyle, PlotLegends -> $legends]
