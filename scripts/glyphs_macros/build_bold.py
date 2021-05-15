import copy

BOLD_INSTANCES = ['Eight', 'SemiLight', 'Regular*', 'Ultra']
BOLD_GLYPH_MAPPINGS = {
	'Abold-math': 'A',
	'Bbold-math': 'B',
	'Cbold-math': 'C',
	'Dbold-math': 'D',
	'Ebold-math': 'E',
	'Fbold-math': 'F',
	'Gbold-math': 'G',
	'Hbold-math': 'H',
	'Ibold-math': 'I',
	'Jbold-math': 'J',
	'Kbold-math': 'K',
	'Lbold-math': 'L',
	'Mbold-math': 'M',
	'Nbold-math': 'N',
	'Obold-math': 'O',
	'Pbold-math': 'P',
	'Qbold-math': 'Q',
	'Rbold-math': 'R',
	'Sbold-math': 'S',
	'Tbold-math': 'T',
	'Ubold-math': 'U',
	'Vbold-math': 'V',
	'Wbold-math': 'W',
	'Xbold-math': 'X',
	'Ybold-math': 'Y',
	'Zbold-math': 'Z',
	'abold-math': 'a',
	'bbold-math': 'b',
	'cbold-math': 'c',
	'dbold-math': 'd',
	'ebold-math': 'e',
	'fbold-math': 'f',
	'gbold-math': 'g',
	'hbold-math': 'h',
	'ibold-math': 'i',
	'jbold-math': 'j',
	'kbold-math': 'k',
	'lbold-math': 'l',
	'mbold-math': 'm',
	'nbold-math': 'n',
	'obold-math': 'o',
	'pbold-math': 'p',
	'qbold-math': 'q',
	'rbold-math': 'r',
	'sbold-math': 's',
	'tbold-math': 't',
	'ubold-math': 'u',
	'vbold-math': 'v',
	'wbold-math': 'w',
	'xbold-math': 'x',
	'ybold-math': 'y',
	'zbold-math': 'z',
	'u1D6A8': 'Alpha', # 𝚨
	'u1D6A9': 'Beta', # 𝚩
	'u1D6AA': 'Gamma', # 𝚪
	'u1D6AB': 'Delta', # 𝚫
	'u1D6AC': 'Epsilon', # 𝚬
	'u1D6AD': 'Zeta', # 𝚭
	'u1D6AE': 'Eta', # 𝚮
	'u1D6AF': 'Theta', # 𝚯
	'u1D6B0': 'Iota', # 𝚰
	'u1D6B1': 'Kappa', # 𝚱
	'u1D6B2': 'Lambda', # 𝚲
	'u1D6B3': 'Mu', # 𝚳
	'u1D6B4': 'Nu', # 𝚴
	'u1D6B5': 'Xi', # 𝚵
	'u1D6B6': 'Omicron', # 𝚶
	'u1D6B7': 'Pi', # 𝚷
	'u1D6B8': 'Rho', # 𝚸
	'u1D6B9': 'ThetaSymbol', # 𝚹
	'u1D6BA': 'Sigma', # 𝚺
	'u1D6BB': 'Tau', # 𝚻
	'u1D6BC': 'Upsilon', # 𝚼
	'u1D6BD': 'Phi', # 𝚽
	'u1D6BE': 'Chi', # 𝚾
	'u1D6BF': 'Psi', # 𝚿
	'u1D6C0': 'Omega', # 𝛀
	'u1D6C1': 'gradient', # 𝛁
	'u1D6C2': 'alpha', # 𝛂
	'u1D6C3': 'beta', # 𝛃
	'u1D6C4': 'gamma', # 𝛄
	'u1D6C5': 'delta', # 𝛅
	'u1D6C6': 'epsilon', # 𝛆
	'u1D6C7': 'zeta', # 𝛇
	'u1D6C8': 'eta', # 𝛈
	'u1D6C9': 'theta', # 𝛉
	'u1D6CA': 'iota', # 𝛊
	'u1D6CB': 'kappa', # 𝛋
	'u1D6CC': 'lambda', # 𝛌
	'u1D6CD': 'mu', # 𝛍
	'u1D6CE': 'nu', # 𝛎
	'u1D6CF': 'xi', # 𝛏
	'u1D6D0': 'omicron', # 𝛐
	'u1D6D1': 'pi', # 𝛑
	'u1D6D2': 'rho', # 𝛒
	'u1D6D3': 'sigmafinal', # 𝛓
	'u1D6D4': 'sigma', # 𝛔
	'u1D6D5': 'tau', # 𝛕
	'u1D6D6': 'upsilon', # 𝛖
	'u1D6D7': 'phi', # 𝛗
	'u1D6D8': 'chi', # 𝛘
	'u1D6D9': 'psi', # 𝛙
	'u1D6DA': 'omega', # 𝛚
	'u1D6DB': 'partialdiff', # 𝛛
	'u1D6DC': 'epsilonLunateSymbol', # 𝛜
	'u1D6DD': 'thetaSymbol', # 𝛝
	'u1D6DE': 'kappaSymbol', # 𝛞
	'u1D6DF': 'phiSymbol', # 𝛟
	'u1D6E0': 'rhoSymbol', # 𝛠
	'u1D6E1': 'piSymbol', # 𝛡
	'Abolditalic-math': 'Aitalic-math',
	'Bbolditalic-math': 'Bitalic-math',
	'Cbolditalic-math': 'Citalic-math',
	'Dbolditalic-math': 'Ditalic-math',
	'Ebolditalic-math': 'Eitalic-math',
	'Fbolditalic-math': 'Fitalic-math',
	'Gbolditalic-math': 'Gitalic-math',
	'Hbolditalic-math': 'Hitalic-math',
	'Ibolditalic-math': 'Iitalic-math',
	'Jbolditalic-math': 'Jitalic-math',
	'Kbolditalic-math': 'Kitalic-math',
	'Lbolditalic-math': 'Litalic-math',
	'Mbolditalic-math': 'Mitalic-math',
	'Nbolditalic-math': 'Nitalic-math',
	'Obolditalic-math': 'Oitalic-math',
	'Pbolditalic-math': 'Pitalic-math',
	'Qbolditalic-math': 'Qitalic-math',
	'Rbolditalic-math': 'Ritalic-math',
	'Sbolditalic-math': 'Sitalic-math',
	'Tbolditalic-math': 'Titalic-math',
	'Ubolditalic-math': 'Uitalic-math',
	'Vbolditalic-math': 'Vitalic-math',
	'Wbolditalic-math': 'Witalic-math',
	'Xbolditalic-math': 'Xitalic-math',
	'Ybolditalic-math': 'Yitalic-math',
	'Zbolditalic-math': 'Zitalic-math',
	'abolditalic-math': 'aitalic-math',
	'bbolditalic-math': 'bitalic-math',
	'cbolditalic-math': 'citalic-math',
	'dbolditalic-math': 'ditalic-math',
	'ebolditalic-math': 'eitalic-math',
	'fbolditalic-math': 'fitalic-math',
	'gbolditalic-math': 'gitalic-math',
	'hbolditalic-math': 'planckconstant',
	'ibolditalic-math': 'iitalic-math',
	'jbolditalic-math': 'jitalic-math',
	'kbolditalic-math': 'kitalic-math',
	'lbolditalic-math': 'litalic-math',
	'mbolditalic-math': 'mitalic-math',
	'nbolditalic-math': 'nitalic-math',
	'obolditalic-math': 'oitalic-math',
	'pbolditalic-math': 'pitalic-math',
	'qbolditalic-math': 'qitalic-math',
	'rbolditalic-math': 'ritalic-math',
	'sbolditalic-math': 'sitalic-math',
	'tbolditalic-math': 'titalic-math',
	'ubolditalic-math': 'uitalic-math',
	'vbolditalic-math': 'vitalic-math',
	'wbolditalic-math': 'witalic-math',
	'xbolditalic-math': 'xitalic-math',
	'ybolditalic-math': 'yitalic-math',
	'zbolditalic-math': 'zitalic-math',
	'u1D71C': 'u1D6E2', # 𝜜: 𝛢
	'u1D71D': 'u1D6E3', # 𝜝: 𝛣
	'u1D71E': 'u1D6E4', # 𝜞: 𝛤
	'u1D71F': 'u1D6E5', # 𝜟: 𝛥
	'u1D720': 'u1D6E6', # 𝜠: 𝛦
	'u1D721': 'u1D6E7', # 𝜡: 𝛧
	'u1D722': 'u1D6E8', # 𝜢: 𝛨
	'u1D723': 'u1D6E9', # 𝜣: 𝛩
	'u1D724': 'u1D6EA', # 𝜤: 𝛪
	'u1D725': 'u1D6EB', # 𝜥: 𝛫
	'u1D726': 'u1D6EC', # 𝜦: 𝛬
	'u1D727': 'u1D6ED', # 𝜧: 𝛭
	'u1D728': 'u1D6EE', # 𝜨: 𝛮
	'u1D729': 'u1D6EF', # 𝜩: 𝛯
	'u1D72A': 'u1D6F0', # 𝜪: 𝛰
	'u1D72B': 'u1D6F1', # 𝜫: 𝛱
	'u1D72C': 'u1D6F2', # 𝜬: 𝛲
	'u1D72D': 'u1D6F3', # 𝜭: 𝛳
	'u1D72E': 'u1D6F4', # 𝜮: 𝛴
	'u1D72F': 'u1D6F5', # 𝜯: 𝛵
	'u1D730': 'u1D6F6', # 𝜰: 𝛶
	'u1D731': 'u1D6F7', # 𝜱: 𝛷
	'u1D732': 'u1D6F8', # 𝜲: 𝛸
	'u1D733': 'u1D6F9', # 𝜳: 𝛹
	'u1D734': 'u1D6FA', # 𝜴: 𝛺
	'u1D735': 'u1D6FB', # 𝜵: 𝛻
	'u1D736': 'u1D6FC', # 𝜶: 𝛼
	'u1D737': 'u1D6FD', # 𝜷: 𝛽
	'u1D738': 'u1D6FE', # 𝜸: 𝛾
	'u1D739': 'u1D6FF', # 𝜹: 𝛿
	'u1D73A': 'u1D700', # 𝜺: 𝜀
	'u1D73B': 'u1D701', # 𝜻: 𝜁
	'u1D73C': 'u1D702', # 𝜼: 𝜂
	'u1D73D': 'u1D703', # 𝜽: 𝜃
	'u1D73E': 'u1D704', # 𝜾: 𝜄
	'u1D73F': 'u1D705', # 𝜿: 𝜅
	'u1D740': 'u1D706', # 𝝀: 𝜆
	'u1D741': 'u1D707', # 𝝁: 𝜇
	'u1D742': 'u1D708', # 𝝂: 𝜈
	'u1D743': 'u1D709', # 𝝃: 𝜉
	'u1D744': 'u1D70A', # 𝝄: 𝜊
	'u1D745': 'u1D70B', # 𝝅: 𝜋
	'u1D746': 'u1D70C', # 𝝆: 𝜌
	'u1D747': 'u1D70D', # 𝝇: 𝜍
	'u1D748': 'u1D70E', # 𝝈: 𝜎
	'u1D749': 'u1D70F', # 𝝉: 𝜏
	'u1D74A': 'u1D710', # 𝝊: 𝜐
	'u1D74B': 'u1D711', # 𝝋: 𝜑
	'u1D74C': 'u1D712', # 𝝌: 𝜒
	'u1D74D': 'u1D713', # 𝝍: 𝜓
	'u1D74E': 'u1D714', # 𝝎: 𝜔
	'u1D74F': 'u1D715', # 𝝏: 𝜕
	'u1D750': 'u1D716', # 𝝐: 𝜖
	'u1D751': 'u1D717', # 𝝑: 𝜗
	'u1D752': 'u1D718', # 𝝒: 𝜘
	'u1D753': 'u1D719', # 𝝓: 𝜙
	'u1D754': 'u1D71A', # 𝝔: 𝜚
	'u1D755': 'u1D71B', # 𝝕: 𝜛
	'u1D7CA': 'Digamma',
	'u1D7CB': 'digamma',
	'u1D7CE': 'zero.tf',
	'u1D7CF': 'one.tf',
	'u1D7D0': 'two.tf',
	'u1D7D1': 'three.tf',
	'u1D7D2': 'four.tf',
	'u1D7D3': 'five.tf',
	'u1D7D4': 'six.tf',
	'u1D7D5': 'seven.tf',
	'u1D7D6': 'eight.tf',
	'u1D7D7': 'nine.tf',
}

interpolated_fonts = []
for instance_name in BOLD_INSTANCES:
	instance = next(i for i in Font.instances if i.name == instance_name)
	print('Generating instance {}...'.format(instance))
	interpolated_fonts.append(instance.interpolatedFont)

for target, source in BOLD_GLYPH_MAPPINGS.items():
	print('{} <- {}'.format(target, source))
	layers = Font.glyphs[target].layers
	for layer, interpolated_font in zip(layers, interpolated_fonts):
		source_layer = interpolated_font.glyphs[source].layers[0]
		source_layer.decomposeComponents()
		layer.shapes = []
		for path in source_layer.paths:
			layer.shapes.append(copy.copy(path))
		layer.width = source_layer.width
