'''Build FiraMath.glyphspackage.
'''

import copy
import functools
import multiprocessing
import os
import sys
import time

import fontmake
from fontmake.font_project import FontProject, GLYPHS_PREFIX, GLYPH_EXPORT_KEY, PUBLIC_PREFIX
from fontmake.instantiator import Instantiator

import fontTools
from fontTools.designspaceLib import DesignSpaceDocument, InstanceDescriptor
from fontTools.ttLib import TTFont
from fontTools.ttLib.ttFont import newTable

import glyphsLib
from glyphsLib import GSComponent, GSFont, GSGlyph, GSLayer, GSNode, GSPath, glyphdata
from glyphsLib.parser import Parser

import toml

from math_table import MathTable, MathTableInstantiator


class Font:

    def __init__(self, path: str):
        self.font = self._load(path)
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
        self.production_names: dict[str, str] = {
            g.name: glyphdata.get_glyph(g.name).production_name
            for g in self.font.glyphs
        }
        self._decompose_smart_comp()

    @staticmethod
    def _load(path: str) -> GSFont:
        '''Load `.glyphspackage` bundle.
        See [googlefonts/glyphsLib#643](https://github.com/googlefonts/glyphsLib/issues/643).
        '''
        with open(os.path.join(path, 'fontinfo.plist'), 'r') as fontinfo_plist:
            fontinfo = fontinfo_plist.read()
        with open(os.path.join(path, 'order.plist'), 'r') as order_plist:
            order = Parser().parse(order_plist.read())
        insert_pos = fontinfo.find('instances = (')
        glyphs = ',\n'.join(Font._read_glyph(path, name) for name in order)
        glyphs = f'glyphs = (\n{glyphs}\n);\n'
        return glyphsLib.loads(fontinfo[:insert_pos] + glyphs + fontinfo[insert_pos:-1])

    @staticmethod
    def _read_glyph(path: str, name: str) -> str:
        if name == '.notdef':
            file_name = '_notdef.glyph'
        else:
            file_name = ''.join(c + '_' if c.isupper() else c for c in name) + '.glyph'
        with open(os.path.join(path, 'glyphs', file_name), 'r') as f:
            return f.read()[:-1]

    def _decompose_smart_comp(self):
        '''Decompose smart components.
        See [googlefonts/glyphsLib#91](https://github.com/googlefonts/glyphsLib/issues/91).
        '''
        # The smart glyphs should be decomposed first.
        for glyph in filter(self._is_smart_glyph, self.font.glyphs):
            for layer in glyph.layers:
                to_be_removed = []
                for comp in layer.components:
                    if self._is_smart_component(comp):
                        paths = self._smart_component_to_paths(comp)
                    else:
                        paths = self._component_to_paths(comp)
                    layer.paths.extend(paths)
                    to_be_removed.append(comp)
                layer._shapes = [s for s in layer._shapes if s not in to_be_removed]
        for glyph in filter(lambda g: not self._is_smart_glyph(g), self.font.glyphs):
            for layer in glyph.layers:
                to_be_removed = []
                for comp in layer.components:
                    if comp.smartComponentValues:
                        paths = self._smart_component_to_paths(comp)
                        layer.paths.extend(paths)
                        to_be_removed.append(comp)
                layer._shapes = [s for s in layer._shapes if s not in to_be_removed]

    @staticmethod
    def _is_smart_glyph(glyph: GSGlyph) -> bool:
        return glyph.smartComponentAxes != []

    @staticmethod
    def _is_smart_component(comp: GSComponent) -> bool:
        return Font._is_smart_glyph(comp.component)

    @staticmethod
    def _smart_component_to_paths(comp: GSComponent) -> list[GSPath]:
        '''Return the paths of a smart component `comp` by interpolating between two layers.
        Note that we only consider single smart component axis here.
        '''
        values: dict = comp.smartComponentValues
        master_id: str = comp.parent.associatedMasterId
        ref_glyph: GSGlyph = comp.component
        if len(values) == 0:
            interpolation_value = 0
            def _is_part_n(layer, n):
                return (
                    layer.associatedMasterId == master_id and
                    layer.partSelection[next(iter(layer.partSelection.keys()))] == n
                )
        elif len(values) == 1:
            key, value = next(iter(values.items()))
            interpolation_value = next(
                Font._rescale(value, axis.bottomValue, axis.topValue)
                for axis in ref_glyph.smartComponentAxes if axis.name == key
            )
            def _is_part_n(layer, n):
                return layer.associatedMasterId == master_id and layer.partSelection[key] == n
        else:
            raise ValueError('We only support single smart component axis!')
        layer_0: GSLayer = next(layer for layer in ref_glyph.layers if _is_part_n(layer, 1))
        layer_1: GSLayer = next(layer for layer in ref_glyph.layers if _is_part_n(layer, 2))
        paths = []
        for path_0, path_1 in zip(layer_0.paths, layer_1.paths):
            path = Font._interpolate_path(path_0, path_1, interpolation_value)
            path.applyTransform(comp.transform)
            paths.append(path)
        return paths

    @staticmethod
    def _rescale(x, bottom, top):
        '''Return rescaled `x` to run from 0 to 1 over the range `bottom` to `top`.'''
        return (x - bottom) / (top - bottom)

    @staticmethod
    def _interpolate_path(path_0: GSPath, path_1: GSPath, value) -> GSPath:
        new_path = copy.copy(path_0)
        new_path.nodes = []
        for node_0, node_1 in zip(path_0.nodes, path_1.nodes):
            new_path.nodes.append(Font._interpolate_node(node_0, node_1, value))
        return new_path

    @staticmethod
    def _interpolate_node(node_0: GSNode, node_1: GSNode, value) -> GSNode:
        position = (
            round(node_0.position.x * (1 - value) + node_1.position.x * value),
            round(node_0.position.y * (1 - value) + node_1.position.y * value),
        )
        return GSNode(position, type=node_0.type, smooth=node_0.smooth)

    @staticmethod
    def _component_to_paths(comp: GSComponent) -> list[GSPath]:
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

    def to_ufos(self, interpolate: bool = True, default_index: int = None) -> list:
        master_ufos, instance_data = glyphsLib.to_ufos(self.font, include_instances=True)
        if not interpolate:
            return master_ufos
        designspace = self._to_designspace(instance_data)
        if default_index:
            designspace.default = designspace.sources[default_index]
        else:
            designspace.default = next(
                (s for s in designspace.sources if s.styleName == 'Regular'),
                designspace.sources[0]
            )
        for axis_index, _ in enumerate(designspace.axes):
            positions = [i.axes[axis_index] for i in self.font.instances]
            designspace.axes[axis_index].map = None
            designspace.axes[axis_index].maximum = max(positions)
            designspace.axes[axis_index].minimum = min(positions)
            designspace.axes[axis_index].default = next(
                i.axes[axis_index] for i in self.font.instances if isinstance(i.weight, str)
            )
        instantiator = Instantiator.from_designspace(designspace)
        return [self._generate_instance(instantiator, i) for i in designspace.instances]

    @staticmethod
    def _to_designspace(instance_data: dict) -> DesignSpaceDocument:
        designspace = instance_data['designspace']
        for instance, data in zip(
            designspace.instances,
            (i for i in instance_data['data'] if i.active),
        ):
            weight_value = 400 if data.weight == 'Regular' else data.weight
            instance.lib[GLYPHS_PREFIX + 'weightValue'] = weight_value
        return designspace

    @staticmethod
    def _generate_instance(instantiator: Instantiator, instance: InstanceDescriptor):
        ufo = instantiator.generate_instance(instance)
        ufo.info.openTypeOS2WeightClass = instance.lib[GLYPHS_PREFIX + 'weightValue']
        if custom_parameters := instance.lib.get(GLYPHS_PREFIX + 'customParameters'):
            if remove_glyphs := dict(custom_parameters).get('Remove Glyphs'):
                ufo.lib[PUBLIC_PREFIX + 'skipExportGlyphs'] = remove_glyphs
        for glyph in (g for g in ufo if '.BRACKET.' in g.name):
            glyph.lib[GLYPH_EXPORT_KEY] = False
        return ufo

    def add_math_table(self, toml_path: str, input_dir: str, output_dir: str = None):
        if not output_dir:
            output_dir = input_dir
        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)
        self._parse_math_table(toml_path)
        for style in self.interpolations:
            font_file_name = self._font_file_name(style)
            eprint(f'=> {font_file_name}')
            input_path = os.path.join(input_dir, font_file_name)
            output_path = os.path.join(output_dir, font_file_name)
            self._write_math_table(style, input_path, output_path)
            self._normalize_glyph_names(output_path, output_path)

    def _parse_math_table(self, toml_path: str):
        master_data = self._parse_master_math_table(toml_path)
        self.math_tables = {
            style: MathTableInstantiator(
                master_data,
                interpolation,
                self._removed_glyphs(style),
            ).generate()
            for style, interpolation in self.interpolations.items()
        }

    def _removed_glyphs(self, style: str):
        instance = next(i for i in self.font.instances if i.name == style)
        return instance.customParameters['Remove Glyphs']

    def _parse_master_math_table(self, toml_path: str) -> dict:
        data = toml.load(toml_path)
        glyph_info = data['MathGlyphInfo']
        variants = data['MathVariants']
        for name in glyph_info:
            for glyph, values in self._get_all_user_data(name).items():
                if len(values) != self._masters_num:
                    eprint(
                        f'Warning: glyph "{glyph}" has incomplete '
                        f'MathGlyphInfo ({name}: {values}).'
                    )
                    values = [values[0]] * self._masters_num
                glyph_info[name][glyph] = values
        for glyph, value in variants['HorizontalVariants'].items():
            variants['HorizontalVariants'][glyph] = {
                var: self._advances(var, 'H', plus_1=True)
                for var in (glyph + suffix for suffix in value['suffixes'])
            }
        for glyph, value in variants['VerticalVariants'].items():
            variants['VerticalVariants'][glyph] = {
                var: self._advances(var, 'V', plus_1=True)
                for var in (glyph + suffix for suffix in value['suffixes'])
            }
        for glyph, value in variants['HorizontalComponents'].items():
            variants['HorizontalComponents'][glyph]['parts'] = [
                part | self._variant_part(part['name'], 'H') for part in value['parts']
            ]
        for glyph, value in variants['VerticalComponents'].items():
            variants['VerticalComponents'][glyph]['parts'] = [
                part | self._variant_part(part['name'], 'V') for part in value['parts']
            ]
        return data

    def _get_all_user_data(self, name: str) -> dict[str, list]:
        # Uncapitalize: 'TopAccent' -> 'topAccent', etc.
        name = name[0].lower() + name[1:]
        mappings = {}
        for glyph in (g for g in self.font.glyphs if g.export):
            if values := self._get_user_data(glyph, name):
                mappings[glyph.name] = values
        return mappings

    def _get_user_data(self, glyph: GSGlyph, name: str) -> list:
        values = []
        for layer in self._master_layers(glyph.layers):
            # Assume there is only one `name` in layer.userData
            try:
                data = next(d for d in layer.userData if name in d)
                values.append(data[name])
            except StopIteration:
                pass
        return values

    def _master_layers(self, layers) -> list[GSLayer]:
        return sorted(
            (l for l in layers if l.associatedMasterId == l.layerId),
            key=lambda l: self._master_id_indices[l.associatedMasterId]
        )

    def _advances(self, glyph: str, direction: str, plus_1: bool = False) -> list:
        result = []
        for layer in self._master_layers(self.font.glyphs[glyph].layers):
            size = layer.bounds.size
            advance = size.width if direction == 'H' else size.height
            result.append(abs(round(advance)))
        if plus_1:
            return [i + 1 for i in result]
        return result

    def _variant_part(self, glyph: str, direction: str) -> dict[str, list]:
        result = {
            name: self._get_user_data(self.font.glyphs[glyph], name)
            for name in ['startConnector', 'endConnector']
        }
        result['fullAdvance'] = self._advances(glyph, direction)
        return result

    def _font_file_name(self, style: str) -> str:
        font_name = self.font.familyName.replace(' ', '')
        return f'{font_name}-{style}.otf'

    def _write_math_table(self, style: str, input_path: str, output_path: str):
        with TTFont(input_path) as tt_font:
            tt_font['MATH'] = newTable('MATH')
            tt_font['MATH'].table = self.math_tables[style].encode()
            tt_font.save(output_path)

    def _normalize_glyph_names(self, input_path: str, output_path: str):
        '''Normalize glyph names using AGL convention.'''
        with TTFont(input_path) as tt_font:
            cff = tt_font['CFF '].cff
            cff.strings.strings = list(map(self._normalize_string, cff.strings.strings))
            tt_font.save(output_path)

    def _normalize_string(self, s: str) -> str:
        # An *ad hoc* treatment for copyright string.
        if 'Copyright Copyright' in s:
            s = s.replace('Copyright Copyright', 'Copyright')  # For U+00A9 `©`
            s = s.replace('?', '-')  # For U+2013 `–`
            return s
        # For glyph names
        return self.production_names.get(s, s)


class Timer:

    def __init__(self, name=None):
        self.name = name
        self.start_time = None

    def __enter__(self):
        if self.name:
            eprint(self.name)
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        t = time.time() - self.start_time
        if t < 60:
            eprint(f'Elapsed: {t:.3f}s\n')
        else:
            eprint(f'Elapsed: {int(t) // 60}min{(t % 60):.3f}s\n')


def eprint(*values, sep: str = ' ', end: str = '\n'):
    '''Print message to `stderr`.'''
    print(*values, sep=sep, end=end, file=sys.stderr)


def build(input_path: str, toml_path: str, output_dir: str, parallel: bool = True):
    '''Build fonts from Glyphs source.

    1. Load the `.glyphspackage` directory into a `GSFont` object with preprocessing
    2. Convert the `GSFont` into a list of UFO objects and perform interpolation
    3. Generate `.otf` font files
    4. Add OpenType MATH table and normalize glyph names
    '''
    eprint(
        f'Python:    {sys.version.split()[0]}\n'
        f'fontmake:  {fontmake.__version__}\n'
        f'fontTools: {fontTools.__version__}\n'
        f'glyphsLib: {glyphsLib.__version__}\n'
        f'CPU count: {multiprocessing.cpu_count()}\n'
    )
    with Timer(f'Parsing input file "{input_path}"...'):
        font = Font(input_path)
    with Timer('Generating UFO...'):
        ufos = font.to_ufos()
    with Timer('Generating OTF...'):
        _build = functools.partial(_build_otf, output_dir=output_dir)
        if parallel:
            with multiprocessing.Pool() as p:
                p.map(_build, ufos)
        else:
            _build_otf(ufos, output_dir)
    with Timer('Adding MATH table...'):
        font.add_math_table(toml_path, input_dir=output_dir)


def _build_otf(ufo, output_dir):
    ufos = ufo if isinstance(ufo, list) else [ufo]
    FontProject().save_otfs(ufos, output_dir=output_dir, optimize_cff=2)


if __name__ == '__main__':
    build('src/FiraMath.glyphspackage', toml_path='src/FiraMath.toml', output_dir='build/')
