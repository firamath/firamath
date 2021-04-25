def getTopAccent(layer):
	if topAnchor := layer.anchors['top']:
		return topAnchor.position.x
	if layer.components:
		if topAnchor := layer.components[0].componentLayer.anchors['top']:
			return topAnchor.position.x
	top = layer.bounds.origin.y + layer.bounds.size.height
	topNodes = []
	for path in layer.paths:
		for node in path.nodes:
			if node.y == top:
				topNodes.append(node.x)
	return sum(topNodes) / len(topNodes)

for l in Font.currentTab.layers:
	if not isinstance(l, GSControlLayer):
		print(l.parent.name)
		for layer in l.parent.layers:
			layer.userData['math'] = {'topAccent': round(getTopAccent(layer))}
