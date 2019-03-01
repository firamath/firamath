(* ::Package:: *)

Remove["Global`*"]
SetDirectory @ ParentDirectory @ NotebookDirectory[];


barChart[$data_] :=
 BarChart[$data,
   ChartLabels -> {
     Placed[ToString /@ Normal @ Keys[$data], {{0.5, 0}, {0.9, 1}}, Rotate[#, 0.3 Pi] &], None},
   ChartLegends -> {"Added", "Placeholder"," Empty"},
   ChartLayout -> "Stacked",
   AspectRatio -> 0.25, ImageSize -> 900, PlotTheme -> "Business"]


path = "./data/glyph-stats.csv";
columns = {3, 5, 6, 7, 8};


keys = AssociationThread[{"Name", "Block", "Type", "Regular", "Others"}
  -> Part[Import[path, {"CSV", "Data", 1}], columns]];
data = Query[All, keys] @
  Import[path, {"CSV", "Dataset", All, columns}, "HeaderLines" -> {1, 0}];


Query[GroupBy["Block"], CountsBy /@ {"Regular", "Others"}] @ data;
Query[All, Merge[{<|"A" -> 0, "B" -> 0, "" -> 0|>, #}, Total]&] /@ % // Normal;
chartData = Values /@ Values[%];
chartLabels = Keys[%%];

Map[Function[x, StringRiffle[ToString/@x, "/"]], Transpose[#]]& /@ chartData;
" (" <> StringRiffle[#, ", "] <> ")" & /@ %;
chartLabels = MapThread[StringJoin, {chartLabels, %}];


barChart[$data_, $labels_, $legend_] :=
  Module[{$width = 2, $sepA = .2, $sepB = .8, $colorIndex = 106,
      rectangle,
      $N, $range, $xTickPos, $xPos, $colors, $bars,
      $rectangle, $ticks},
    rectangle[heights_, x_, w_] :=
      Rectangle[{x, First @ #}, {x + w, Last @ #}] & /@
        Partition[FoldList[Plus, 0, heights], 2, 1];
    $N = Dimensions[$data][[2]];
    $range = Range @ Length @ $data;
    $xTickPos = ($N * ($width + $sepA) - $sepA + $sepB) * $range;
    $xPos = # - (($N+1) * ($width + $sepA) + $width) / 2 + Range[$N] * ($width + $sepA) &
      /@ $xTickPos;
    $colors =  ColorData[$colorIndex] /@ Range[Last @ Dimensions @ $data];
    $bars = MapThread[rectangle[#1, #2, $width] &, {$data, $xPos}, 2];
    
    $rectangle = Flatten @ Map[MapThread[List, {$colors, #}] &, $bars, {2}];
    $ticks = MapThread[Inset[#1, {#2, 0}, {1, 1}] &,
      {Rotate[#, 1.2] & /@ $labels, $xTickPos}];

    Legended[Graphics[{$rectangle, $ticks},
        Axes -> {False, True},
        AxesOrigin -> {Min @ Flatten @ $xPos - $sepB / 2, 0},
        GridLines -> {None, Automatic},
        GridLinesStyle -> Directive[Gray, AbsoluteThickness[1], AbsoluteDashing[{1, 2}]],
        AspectRatio -> 0.3, ImageSize -> 1280],
      Placed[#, Below] & @
       SwatchLegend[$colors, $legend, LegendLayout -> "Row"]]
  ]

barChart[chartData, chartLabels, {"Finished", "Placeholder", "Empty"}]
