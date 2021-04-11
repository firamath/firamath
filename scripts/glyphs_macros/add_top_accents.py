for l in Font.currentTab.layers:
	if not isinstance(l, GSControlLayer):
		print(l.parent.name)
		for layer in l.parent.layers:
			top = layer.bounds.origin.y + layer.bounds.size.height
			topNodes = []
			for path in layer.paths:
				for node in path.nodes:
					if node.y == top:
						topNodes.append(node.x)
			topAccent = round(sum(topNodes) / len(topNodes))
			layer.userData['math'] = {'topAccent': topAccent}
