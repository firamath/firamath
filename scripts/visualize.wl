(* ::Package:: *)

Remove["Global`*"]
SetDirectory @ ParentDirectory @ NotebookDirectory[];


(* ::Section:: *)
(*Python part*)


fontPath[$weight_] :=
  FileNameJoin[{Directory[], "src", "FiraMath-" <> $weight <> ".sfd"}]


pythonCode[$font_, $glyphName_] :=
  StringTemplate[StringRiffle[#, "\n"] & @
    {
      (* A simple Python script use FontForge's API *)
      "from __future__ import print_function",
      "import fontforge as ff",
      "font = ff.open(\"`$fontName`\")",
      "layer = font[\"`$glyphName`\"].layers[1]",
      "print([[[p.x, p.y, int(p.on_curve)]
               for p in contour] for contour in layer])"
    }
  ] @ <|"$fontName" -> $font, "$glyphName" -> $glyphName|>


(* See https://mathematica.stackexchange.com/q/174964 *)
If[$OperatingSystem == "Unix",
  $env = <|"libz.so.1" -> "/usr/lib64/libz.so.1",
           "PATH" -> Environment["PATH"]|>,
  $env = Inherited];
runPython[$code_] := RunProcess[{"python", "-c", $code}, ProcessEnvironment -> $env]


(* ::Section:: *)
(*Parse points and curves*)


parseGlyph[$font_, $glyphName_] :=
  Module[{$output},
    $output = runPython[pythonCode[$font, $glyphName]]["StandardOutput"];
    $parseGlyph @ ImportString[$output, "RawJSON"]
  ]
$parseGlyph[$glyph_] := Merge[$parseContour /@ $glyph, Catenate]
$parseContour[$c_] :=
  Module[{$points, $ctrlPoints, $linePoints, $curvePoints},
    $points      = Select[$c, Last[#] == 1 &];
    $ctrlPoints  = Select[$c, Last[#] == 0 &];
    $linePoints  = Select[$curveAux[$c, 2], (#[[1, 3]] == #[[2, 3]] == 1) &];
    $curvePoints = Select[$curveAux[$c, 4], (#[[1, 3]] == 1 && #[[2, 3]] == #[[3, 3]] == 0) &];
    <|
      "Points"      -> Point /@ $coord @ $points,
      "Lines"       -> Line /@ $coord @ $linePoints,
      "Curves"      -> BezierCurve /@ $coord @ $curvePoints,
      "Ctrl.Points" -> Point /@ $coord @ $ctrlPoints,
      "Ctrl.Lines"  -> Line /@ Partition[Flatten[$coord @ $curvePoints, 1], 2]
    |>
  ]
$curveAux[$c_, $n_] :=
  Partition[PadRight[$c, Length[$c] + 1, "Periodic"], $n, 1]
$coord[$list_] := ReplaceAll[#, {x_, y_, c_} -> {x, y}] & /@ $list


(* ::Section:: *)
(*Plot*)


weightList = {"Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular", "Medium",
              "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"};


AbsoluteTiming[p = ParallelMap[parseGlyph[fontPath[#], "uni0032"]&, weightList];]
{Gray, #["Lines"], #["Curves"]}& /@ p //Graphics[#, PlotRange->{{-200,800},{-200,1000}}, Frame->True]&
