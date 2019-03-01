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


Query[GroupBy["Block"], CountsBy["Regular"]] @ data;
Query[All, Merge[{<|"A" -> 0, "B" -> 0, "" -> 0|>, #}, Total]&] @ % // Dataset
% // barChart

Query[GroupBy["Block"], CountsBy["Others"]] @ data;
Query[All, Merge[{<|"A" -> 0, "B" -> 0, "" -> 0|>, #}, Total]&] @ % // Dataset
% // barChart
