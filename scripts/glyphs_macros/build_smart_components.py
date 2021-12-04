suffix_list = [''] + [f'.size{i:02}' for i in range(1, 16)]
basename1 = 'lightlefttortoiseshellbracketornament'
basename2 = 'lightrighttortoiseshellbracketornament'

for i, suffix in enumerate(suffix_list):
	glyph1 = Font.glyphs[basename1 + suffix]
	for layer in glyph1.layers:
		print(layer)
		component = GSComponent('_smart.' + basename1)
		component.automaticAlignment = True
		component.smartComponentValues['size'] = i
		layer.shapes = [component]
	glyph2 = Font.glyphs[basename2 + suffix]
	for layer in glyph2.layers:
		print(layer)
		component = GSComponent(basename1 + suffix)
		component.scale = (-1, 1)
		layer.shapes = [component]
		for shape in layer.shapes:
			shape.automaticAlignment = True
