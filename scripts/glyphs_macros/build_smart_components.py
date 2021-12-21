variantNum = 15
sizeList   = [1280 + 320 * i for i in range(variantNum)]
suffixList = [""] + [f".size{i + 1:02}" for i in range(variantNum)]
basename1  = "bracketleft"
basename2  = "bracketright"
smartGlyph = Font.glyphs["_smart." + basename1]
isVertical = True

zeroSizeList = []
for layer in smartGlyph.layers:
	if layer.isMasterLayer:
		if isVertical:
			zeroSizeList.append(layer.bounds.size.height)
		else:
			zeroSizeList.append(layer.bounds.size.width)

for i, suffix in enumerate(suffixList):
	glyph1 = Font.glyphs[basename1 + suffix]
	for layer, zeroSize in zip(glyph1.layers, zeroSizeList):
		print(layer)
		size = (([zeroSize] + sizeList)[i] - zeroSize) / (sizeList[-1] - zeroSize)
		component = GSComponent(smartGlyph)
		component.automaticAlignment = True
		if size:
			component.smartComponentValues["size"] = size
		layer.shapes = [component]
	glyph2 = Font.glyphs[basename2 + suffix]
	for layer in glyph2.layers:
		print(layer)
		component = GSComponent(basename1 + suffix)
		component.scale = (-1, 1)
		layer.shapes = [component]
		for shape in layer.shapes:
			shape.automaticAlignment = True
