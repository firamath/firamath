names = [
	'lightlefttortoiseshellbracketornament',
]

for name in names:
	name = '_smart.' + name
	if name not in Font.glyphs:
		newGlyph = Font.glyphs['_smart.parenleft'].copy()
		newGlyph.name = name
		for layer in newGlyph.layers:
			layer.shapes.clear()
			layer.width = 600
		Font.glyphs.append(newGlyph)
