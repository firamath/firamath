(* ::Package:: *)

SetDirectory[NotebookDirectory[]];


data = Import["../data/interpolation-coefficients.txt", "Table"] /.
  {label_, y_} -> (y -> label);
Show[
  ListLinePlot[data, PlotRange -> {-0.1, 1.1}, PlotTheme -> "Business"],
  Plot[(x - 1) / (Length @ data - 1), {x, 1, Length @ data}, PlotStyle -> {Gray, Dashed}]]
