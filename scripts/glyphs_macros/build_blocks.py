coords = {
	'upperHalfBlock':          ((  1, 1/2), (  1,   1), (  0,   1), (  0, 1/2)),
	'lowerOneEighthBlock':     ((  1,   0), (  1, 1/8), (  0, 1/8), (  0,   0)),
	'lowerOneQuarterBlock':    ((  1,   0), (  1, 2/8), (  0, 2/8), (  0,   0)),
	'lowerThreeEighthsBlock':  ((  1,   0), (  1, 3/8), (  0, 3/8), (  0,   0)),
	'lowerHalfBlock':          ((  1,   0), (  1, 4/8), (  0, 4/8), (  0,   0)),
	'lowerFiveEighthsBlock':   ((  1,   0), (  1, 5/8), (  0, 5/8), (  0,   0)),
	'lowerThreeQuartersBlock': ((  1,   0), (  1, 6/8), (  0, 6/8), (  0,   0)),
	'lowerSevenEighthsBlock':  ((  1,   0), (  1, 7/8), (  0, 7/8), (  0,   0)),
	'fullBlock':               ((  1,   0), (  1,   1), (  0,   1), (  0,   0)),
	'leftSevenEighthsBlock':   ((7/8,   0), (7/8,   1), (  0,   1), (  0,   0)),
	'leftThreeQuartersBlock':  ((6/8,   0), (6/8,   1), (  0,   1), (  0,   0)),
	'leftFiveEighthsBlock':    ((5/8,   0), (5/8,   1), (  0,   1), (  0,   0)),
	'leftBlock':               ((4/8,   0), (4/8,   1), (  0,   1), (  0,   0)),
	'leftThreeEighthsBlock':   ((3/8,   0), (3/8,   1), (  0,   1), (  0,   0)),
	'leftOneQuarterBlock':     ((2/8,   0), (2/8,   1), (  0,   1), (  0,   0)),
	'leftOneEighthBlock':      ((1/8,   0), (1/8,   1), (  0,   1), (  0,   0)),
	'rightBlock':              ((  1,   0), (  1,   1), (1/2,   1), (1/2,   0)),
	'upperOneEighthBlock':     ((  1, 7/8), (  1,   1), (  0,   1), (  0, 7/8)),
	'rightOneEighthBlock':     ((  1,   0), (  1,   1), (7/8,   1), (7/8,   0)),
	'lowerLeftBlock':          ((1/2,   0), (1/2, 1/2), (  0, 1/2), (  0,   0)),
	'upperLeftBlock':          ((1/2, 1/2), (1/2,   1), (  0,   1), (  0, 1/2)),
}

width = 600

for name, coord in coords.items():
	for layer in Font.glyphs[name].layers:
		height = layer.ascender - layer.descender
		path = GSPath()
		for i in range(4):
			x = width * coord[i][0]
			y = layer.descender + height * coord[i][1]
			node = GSNode((x, y), type=LINE)
			path.nodes.append(node)
		path.closed = True
		layer.shapes = [path]
