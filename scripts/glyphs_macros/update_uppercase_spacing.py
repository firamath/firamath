delta = {'Light': 10, 'SemiLight': 12, 'Regular': 16, 'Bold': 20}

for layer in Font.currentTab.layers:
	if not isinstance(layer, GSControlLayer):
		glyph = layer.parent
		print(glyph)
		if not glyph.leftMetricsKey:
			layer.LSB += delta[layer.name]
		if not glyph.rightMetricsKey:
			layer.RSB += delta[layer.name]
