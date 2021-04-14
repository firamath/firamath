'''Build FiraMath.glyphspackage.
'''

import copy
import os
import sys
import time

from fontmake.font_project import FontProject
from fontmake.instantiator import Instantiator

import fontTools
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.ttFont import newTable

import glyphsLib
from glyphsLib import GSComponent, GSFont, GSGlyph, GSLayer, GSNode, GSPath
from glyphsLib.parser import Parser

import toml


class Font:

    def __init__(self, path: str):
        with open(os.path.join(path, 'fontinfo.plist'), 'r') as fontinfo_plist:
            fontinfo = fontinfo_plist.read()
        with open(os.path.join(path, 'order.plist'), 'r') as order_plist:
            order = Parser().parse(order_plist.read())
        insert_pos = fontinfo.find('instances = (')
        glyphs_str = 'glyphs = (\n{}\n);\n'.format(
            ',\n'.join(self._read_glyph(path, name) for name in order)
        )
        self.font: GSFont = Parser(current_type=GSFont).parse(
            fontinfo[:insert_pos] + glyphs_str + fontinfo[insert_pos:-1]
        )
        self.math_tables: dict[str, MathTable] = {}
        masters = sorted(self.font.masters, key=lambda m: m.weightValue)
        self._masters_num = len(masters)
        self._master_id_indices = {m.id: i for i, m in enumerate(masters)}
        self.interpolations: dict[str, tuple] = {
            i.name: [
                (self._master_id_indices[id], value)
                for id, value in i.instanceInterpolations.items()
            ]
            for i in self.font.instances if i.active
        }
        self._fix_export()
        self._decompose_smart_comp()

    def _read_glyph(self, path: str, name: str):
        if name == '.notdef':
            file_name = '_notdef.glyph'
        else:
            file_name = ''.join(c + '_' if c.isupper() else c for c in name) + '.glyph'
        with open(os.path.join(path, 'glyphs', file_name), 'r') as f:
            return f.read()[:-1]

    def _fix_export(self):
        '''Change `... = 0` to `... = False`.'''
        for glyph in (g for g in self.font.glyphs if g.export == 0):
            glyph.export = False
        for instance in (i for i in self.font.instances if i.active == 0):
            instance.active = False

    def _decompose_smart_comp(self):
        # The smart glyphs should be decomposed first.
        for glyph in (g for g in self.font.glyphs if g.category == 'Smart Glyph'):
            for layer in glyph.layers:
                to_be_removed = []
                for comp in layer.components:
                    # If `Group == 1`, then it's a nested component that is not smart.
                    if 'Group' in comp.smartComponentValues:
                        paths = self._comp_to_paths(comp)
                    else:
                        paths = self._smart_comp_to_paths(comp)
                    layer.paths.extend(paths)
                    to_be_removed.append(comp)
                layer._shapes = [s for s in layer._shapes if s not in to_be_removed]
        for glyph in (g for g in self.font.glyphs if g.category != 'Smart Glyph'):
            for layer in glyph.layers:
                to_be_removed = []
                for comp in layer.components:
                    if comp.smartComponentValues:
                        paths = self._smart_comp_to_paths(comp)
                        layer.paths.extend(paths)
                        to_be_removed.append(comp)
                layer._shapes = [s for s in layer._shapes if s not in to_be_removed]

    def _comp_to_paths(self, comp: GSComponent) -> list[GSPath]:
        '''Return the paths of a normal component `comp`, i.e. decompose `comp`.'''
        ref_glyph: GSGlyph = comp.component
        paths = next(
            layer.paths for layer in ref_glyph.layers
            if layer.layerId == comp.parent.associatedMasterId
        )
        result = []
        for path in paths:
            # Manually deepcopy (`copy.deepcopy()` is very slow here).
            new_path = copy.copy(path)
            new_path.nodes = [GSNode(n.position, type=n.type, smooth=n.smooth) for n in path.nodes]
            new_path.applyTransform(comp.transform)
            result.append(new_path)
        return result

    def _smart_comp_to_paths(self, comp: GSComponent) -> list[GSPath]:
        '''Return the paths of a smart component `comp` by interpolating between two layers.
        Note that we only consider single smart component axis here.
        '''
        values: dict = comp.smartComponentValues
        master_id: str = comp.parent.associatedMasterId
        ref_glyph: GSGlyph = comp.component
        if len(values) == 0:
            interpolation_value = 0
            is_part_n = lambda layer, n: \
                layer.associatedMasterId == master_id and \
                layer.partSelection[next(iter(layer.partSelection.keys()))] == n
        elif len(values) == 1:
            key, value = next(iter(values.items()))
            interpolation_value = next(
                self._rescale(value, axis.bottomValue, axis.topValue)
                for axis in ref_glyph.smartComponentAxes if axis.name == key
            )
            is_part_n = lambda layer, n: \
                layer.associatedMasterId == master_id and layer.partSelection[key] == n
        else:
            raise ValueError('We only support single smart component axis!')
        layer_0: GSLayer = next(layer for layer in ref_glyph.layers if is_part_n(layer, 1))
        layer_1: GSLayer = next(layer for layer in ref_glyph.layers if is_part_n(layer, 2))
        paths = []
        for path_0, path_1 in zip(layer_0.paths, layer_1.paths):
            path = self._interpolate_path(path_0, path_1, interpolation_value)
            path.applyTransform(comp.transform)
            paths.append(path)
        return paths

    def _rescale(self, x, min, max):
        '''Return rescaled `x` to run from 0 to 1 over the range `min` to `max`.'''
        return (x - min) / (max - min)

    def _interpolate_path(self, path_0: GSPath, path_1: GSPath, value) -> GSPath:
        new_path = copy.copy(path_0)
        new_path.nodes = []
        for node_0, node_1 in zip(path_0.nodes, path_1.nodes):
            new_path.nodes.append(self._interpolate_node(node_0, node_1, value))
        return new_path

    def _interpolate_node(self, node_0: GSNode, node_1: GSNode, value) -> GSNode:
        position = (
            round(node_0.position.x * (1 - value) + node_1.position.x * value),
            round(node_0.position.y * (1 - value) + node_1.position.y * value),
        )
        return GSNode(position, type=node_0.type, smooth=node_0.smooth)

    def to_ufos(self, interpolate: bool = True, default_index: int = None) -> list:
        ufos, instance_data = glyphsLib.to_ufos(self.font, include_instances=True)
        if not interpolate:
            return ufos
        designspace: DesignSpaceDocument = instance_data['designspace']
        if default_index:
            designspace.default = designspace.sources[default_index]
        else:
            designspace.default = next(
                (s for s in designspace.sources if s.styleName == 'Regular'),
                designspace.sources[0]
            )
        for axis_index in range(len(designspace.axes)):
            positions = [i.axes[axis_index] for i in self.font.instances]
            designspace.axes[axis_index].map = None
            designspace.axes[axis_index].maximum = max(positions)
            designspace.axes[axis_index].minimum = min(positions)
            designspace.axes[axis_index].default = next(
                i.axes[axis_index] for i in self.font.instances if isinstance(i.weight, str)
            )
        instantiator = Instantiator.from_designspace(designspace)
        ufos.extend(map(instantiator.generate_instance, designspace.instances))
        return ufos

    def add_math_table(self, toml_path: str, input_dir: str, output_dir: str = None):
        if not output_dir:
            output_dir = input_dir
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        font_name = self.font.familyName.replace(' ', '')
        self._parse_math_table(toml_path)

        for style in self.interpolations:
            font_file_name = '{}-{}.otf'.format(font_name, style)
            input = os.path.join(input_dir, font_file_name)
            output = os.path.join(output_dir, font_file_name)
            with TTFont(input) as tt_font:
                tt_font['MATH'] = newTable('MATH')
                tt_font['MATH'].table = self.math_tables[style].encode()
                tt_font.save(output)

    def _parse_math_table(self, toml_path: str):
        master_data = self._parse_master_math_table(toml_path)
        for style, interpolation in self.interpolations.items():
            math_table = MathTable()
            _generate = lambda values: round(sum(values[i] * v for i, v in interpolation))
            for name, d in master_data['MathConstants'].items():
                math_table.constants[name] = {
                    'value': _generate(d['value']),
                    'isMathValue': d['isMathValue'],
                }
            for name, d in master_data['MathGlyphInfo'].items():
                math_table.glyph_info[name] = {g: _generate(values) for g, values in d.items()}
            math_table.variants['MinConnectorOverlap'] = \
                _generate(master_data['MathVariants']['MinConnectorOverlap'])
            math_table.variants['HorizontalVariants'] = {
                glyph: {g: _generate(values) for g, values in variants.items()}
                for glyph, variants in master_data['MathVariants']['HorizontalVariants'].items()
            }
            math_table.variants['VerticalVariants'] = {
                glyph: {g: _generate(values) for g, values in variants.items()}
                for glyph, variants in master_data['MathVariants']['VerticalVariants'].items()
            }
            self.math_tables[style] = math_table

    def _parse_master_math_table(self, toml_path: str):
        data = toml.load(toml_path)
        glyph_info = data['MathGlyphInfo']
        variants = data['MathVariants']
        for name in glyph_info:
            for glyph, values in self._get_user_data(name).items():
                if len(values) != self._masters_num:
                    # TODO:
                    print(
                        'Warning: glyph "{}" has incomplete MathGlyphInfo ({}: {}).'.format(
                            glyph, name, values
                        ),
                        file=sys.stderr
                    )
                    values = [values[0]] * self._masters_num
                glyph_info[name][glyph] = values
        for glyph, value in variants['HorizontalVariants'].items():
            variants['HorizontalVariants'][glyph] = {
                var: self._advances(var, 'horizontal')
                for var in (glyph + suffix for suffix in value['suffixes'])
            }
        for glyph, value in variants['VerticalVariants'].items():
            variants['VerticalVariants'][glyph] = {
                var: self._advances(var, 'vertical')
                for var in (glyph + suffix for suffix in value['suffixes'])
            }
        return data

    def _get_user_data(self, name: str):
        # Uncapitalize: 'TopAccent' -> 'topAccent', etc.
        name = name[0].lower() + name[1:]
        mappings = {}
        for glyph in self.font.glyphs:
            values = []
            for layer in self._master_layers(glyph.layers):
                # Assume there is only one `name` in layer.userData
                try:
                    data = next(d for d in layer.userData if name in d)
                    values.append(data[name])
                except StopIteration:
                    pass
            if values:
                mappings[glyph.name] = values
        return mappings

    def _advances(self, glyph: str, direction: str):
        result = []
        for layer in self._master_layers(self.font.glyphs[glyph].layers):
            size = layer.bounds.size
            advance = size.width if direction == 'horizontal' else size.height
            result.append(abs(round(advance)) + 1)
        return result

    def _master_layers(self, layers):
        return sorted(
            (l for l in layers if l.associatedMasterId == l.layerId),
            key=lambda l: self._master_id_indices[l.associatedMasterId]
        )


class MathTable:

    def __init__(self):
        self.constants = {}
        self.glyph_info = {
            'ItalicCorrection': {},
            'TopAccent': {},
            # 'ExtendedShapes': [],
        }
        self.variants = {}

    def encode(self):
        table = otTables.MATH()
        table.Version = 0x00010000
        table.MathConstants = self._encode_constants()
        table.MathGlyphInfo = self._encode_glyph_info()
        table.MathVariants = self._encode_variants()
        return table

    def _encode_constants(self):
        constants = otTables.MathConstants()
        for name, d in self.constants.items():
            value = d['value']
            constants.__setattr__(name, self._math_value(value) if d['isMathValue'] else value)
        return constants

    def _encode_glyph_info(self):
        italic_corr = otTables.MathItalicsCorrectionInfo()
        italic_corr.ItalicsCorrection, italic_corr.Coverage, italic_corr.ItalicsCorrectionCount = \
            self._glyph_info('ItalicCorrection')
        top_accent = otTables.MathTopAccentAttachment()
        top_accent.TopAccentAttachment, top_accent.TopAccentCoverage, top_accent.TopAccentAttachmentCount = \
            self._glyph_info('TopAccent')
        glyph_info = otTables.MathGlyphInfo()
        glyph_info.MathItalicsCorrectionInfo = italic_corr
        glyph_info.MathTopAccentAttachment = top_accent
        glyph_info.ExtendedShapeCoverage = None
        glyph_info.MathKernInfo = None
        return glyph_info

    def _glyph_info(self, name: str):
        return (
            list(map(self._math_value, self.glyph_info[name].values())),
            self._coverage(self.glyph_info[name].keys()),
            len(self.glyph_info[name])
        )

    def _encode_variants(self):
        variants = otTables.MathVariants()
        variants.MinConnectorOverlap = self.variants['MinConnectorOverlap']
        variants.HorizGlyphConstruction, variants.HorizGlyphCoverage, variants.HorizGlyphCount = \
            self._variants('HorizontalVariants')
        variants.VertGlyphConstruction, variants.VertGlyphCoverage, variants.VertGlyphCount = \
            self._variants('VerticalVariants')
        return variants

    def _variants(self, name: str):
        return (
            list(map(self._glyph_construction, self.variants[name].values())),
            self._coverage(self.variants[name].keys()),
            len(self.variants[name])
        )

    def _glyph_construction(self, variants: dict):
        construction = otTables.MathGlyphConstruction()
        construction.GlyphAssembly = None  # TODO:
        construction.VariantCount = len(variants)
        construction.MathGlyphVariantRecord = []
        for glyph, advance in variants.items():
            r = otTables.MathGlyphVariantRecord()
            r.AdvanceMeasurement = advance
            r.VariantGlyph = glyph
            construction.MathGlyphVariantRecord.append(r)
        return construction

    def _math_value(self, value):
        t = otTables.MathValueRecord()
        t.DeviceTable = None
        t.Value = value
        return t

    def _coverage(self, glyphs):
        c = otTables.Coverage()
        c.glyphs = glyphs
        return c


class Timer:

    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        if self.name:
            print(self.name, file=sys.stderr)
        self.start_time = time.time()

    def __exit__(self, type, value, traceback):
        print('Elapsed: {:.3}s\n'.format(time.time() - self.start_time), file=sys.stderr)


def build(input_path: str, toml_path: str, output_dir: str):
    '''Build fonts from Glyphs source.

    1. Read the `.glyphspackage` directory into a `GSFont` object with preprocessing
    2. Convert the `GSFont` into a list of UFO objects and perform interpolation
    3. Generate `.otf` font files
    4. Add the OpenType MATH tables
    '''
    print('Python {}\nfonttools {}\nglyphsLib {}\n'.format(
        sys.version.split()[0],
        fontTools.version,
        glyphsLib.__version__,
    ), file=sys.stderr)
    with Timer('Parsing input file \'{}\'...'.format(input_path)):
        font = Font(input_path)
    with Timer('Generating UFO...'):
        ufos = font.to_ufos()
    with Timer('Generating OTF...'):
        FontProject(verbose='WARNING').build_otfs(ufos, output_dir=output_dir)
    with Timer('Adding MATH table...'):
        font.add_math_table(toml_path, input_dir=output_dir)


if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', toml_path='src/FiraMath.toml', output_dir='build/')
