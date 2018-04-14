(* ::Package:: *)

Remove["Global`*"]


SetDirectory[NotebookDirectory[]];


otfcc$exe          = "..\\tools\\otfccdump.exe";
fira$sfdir         = "..\\fira-math.sfdir";
fira$otf$filename  = "..\\docs\\assets/fira-math.otf";
fira$json$filename = "..\\data\\fira-math.json";
udata$filename     = "..\\data\\UnicodeData.txt";
nudata$filename    = "..\\data\\non-unicode.txt";


(* ::Section:: *)
(*Miscellaneous functions*)


decimalToHexString[$string_] :=
  ToUpperCase @ IntegerString[#, 16] & @ ToExpression @ $string
hexToDecimalString[$string_] :=
  Interpreter["HexInteger"][$string]


paddingZero[$hex_] :=
  If[StringLength[$hex] == 2, "00" <> $hex,
    If[StringLength[$hex] == 3, "0" <> $hex, $hex]]


showTime[$t_, $label_] := Echo[Quantity[$t, "Seconds"], $label]


(* ::Section:: *)
(*Unicode*)


RunProcess[{otfcc$exe, "--pretty", "-o", fira$json$filename, fira$otf$filename}];


cmap$dec = Keys @ Association[Association[Import[fira$json$filename]]["cmap"]];
cmap$hex = decimalToHexString /@ cmap$dec;
Length[cmap$dec]


Import[udata$filename, "Table", "FieldSeparators" -> ";", "Numeric" -> False];
# /. {id_, name_, __} -> {id, name} & /@ %;
Select[%, #[[2]] != "<control>" &];
udata = StringReplace[StartOfString ~~ "0" .. -> ""] /@ %;
Length[udata]


udata$assoc = AssociationThread @@ Transpose[udata];


MapThread[{"Encoding.Hex" -> #1, "Encoding.Dec" -> #2,
           "Unicode.Hex" -> paddingZero[#1], "Unicode.Dec" -> #2,
           "Name" -> udata$assoc @ #1} &,
  {cmap$hex, cmap$dec}];
MapThread[<|#1[[1]], #1[[2]], #1[[3]], #1[[4]], "Index" -> #2, #1[[5]]|> &,
  {%, Range[Length[%]] - 1}];
uni$dataset = Dataset[%];


(* ::Section:: *)
(*Non-Unicode (glyphs variants)*)


nuni = Flatten @ Import[nudata$filename, "Table"];


(* 0x110000 is the beginning of non-unicode *)
With[{$encoding$dec = hexToDecimalString["110000"] + Range[Length[nuni]] - 1},
  With[
    {
      $encoding$hex = decimalToHexString /@ $encoding$dec,
      $index = Length[cmap$dec] + Range[Length[nuni]] - 1
    },
    nuni$dataset = Dataset @
      MapThread[<|"Encoding.Hex" -> #1, "Encoding.Dec" -> ToString[#2],
                  "Unicode.Hex" -> ToString[-1], "Unicode.Dec" -> ToString[-1],
                  "Index" -> #3, "Name" -> #4|> &,
        {$encoding$hex, $encoding$dec, $index, nuni}]
  ]
];


fira$dataset = Join[uni$dataset, nuni$dataset]


(* ::Section:: *)
(*Re-encode and rename*)


unicodeName[$assoc_] := If[StringLength[#] != 5, "uni" <> #, "u" <> #] & @ $assoc["Unicode.Hex"]
(* Add "_" for uXXXX[A-F] *)
unicodeFileName[$assoc_] :=
  StringReplace[unicodeName[$assoc], RegularExpression["^(u[^n].*)(\\D)$"] -> "$1_$2"]


replaceUnicode[$string_, $assoc_] :=
  Module[{$name = unicodeName[$assoc]},
    StringReplace[$string, "StartChar:" ~~ __ ~~ "\nWidth:" ->
         "StartChar: " <> $name <> "\n"
      <> "Encoding: "  <> $assoc["Encoding.Dec"]     <> " "
                       <> $assoc["Unicode.Dec"]      <> " "
                       <> ToString @ $assoc["Index"] <> "\n"
      <> "Width:"]
  ]
replaceNonUnicode[$string_, $assoc_] :=
  StringReplace[$string, "StartChar:" ~~ __ ~~ "\nWidth:" ->
       "StartChar: " <> $assoc["Name"]  <> "\n"
    <> "Encoding: "  <> $assoc["Encoding.Dec"]     <> " "
                     <> $assoc["Unicode.Dec"]      <> " "
                     <> ToString @ $assoc["Index"] <> "\n"
    <> "Width:"]


getAssoc[$name_, $encodings_] :=
  If[$encodings[[2]] != "-1",
    First @ Normal @ fira$dataset[
      Select[#["Encoding.Hex"] == decimalToHexString @ First @ $encodings &]],
    First @ Normal @ fira$dataset[Select[#["Name"] == $name &]]
  ]


processGlyph[$string_] :=
  Module[
    {
      $name = First @ StringCases[$string, "StartChar: " ~~ n__ ~~ "\nEncoding:" -> n],
      $encodings = Flatten @ StringCases[$string,
        "Encoding: " ~~ e : NumberString ~~ Whitespace
                     ~~ u : NumberString ~~ Whitespace
                     ~~ i : NumberString ~~ Whitespace -> {e, u, i}]
    },
    Module[{$assoc = getAssoc[$name, $encodings]},
        If[$assoc["Unicode.Hex"] != "-1",
          {replaceUnicode[$string, $assoc] <> "\n", unicodeFileName[$assoc] <> ".glyph"},
          {replaceNonUnicode[$string, $assoc] <> "\n", $assoc["Name"] <> ".glyph"}]
    ]
  ]


(* ::Section:: *)
(*Run*)


SetDirectory[fira$sfdir];
glyphs = FileNames["*.glyph"];
glyphsCount = Length @ glyphs


(* Import *)
$time = First @ AbsoluteTiming[inputs = ParallelMap[Import[#, "Text"] &, glyphs]];
showTime[$time, "Import time:"];
(* Process *)
$time = First @ AbsoluteTiming[outputs = ParallelMap[processGlyph, inputs]];
showTime[$time, "Process time:"];
(* Export *)
DeleteFile[glyphs];
$time = First @ AbsoluteTiming[
  streams = OpenWrite[#, BinaryFormat -> True] & /@ outputs[[All, 2]] ];
showTime[$time, "Open streams time:"];
$time = First @ AbsoluteTiming[
  MapThread[Export[#1, #2, "Text"] &, {streams, outputs[[All, 1]]}]];
showTime[$time, "Export time:"];
Close /@ streams;
