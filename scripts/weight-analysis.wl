(* ::Package:: *)

SetDirectory[NotebookDirectory[]];


data = Association /@ Association @ Import["../data/weight-analysis.json"];
ticks = Transpose[{Range[Length[#]], #} & @ Keys @ data[["Thin-Ultra"]]];
ListLinePlot[data, PlotRange -> {{0.5, 12.5}, {-0.05, 1.05}},
  LabelingFunction -> (Callout[#] &), LabelStyle -> {FontSize -> 15},
  FrameTicks -> {{Automatic, None}, {ticks, None}},
  PlotTheme -> {"Detailed", "VibrantColor", "OpenMarkers", "ThickLines"},
  ImageSize -> 1000, AspectRatio -> 0.5]
