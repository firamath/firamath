'''OpenType MATH table.
'''

from fontTools.ttLib.tables import otTables


class MathTable:

    def __init__(self):
        self.constants = {}
        self.glyph_info = {
            'ItalicCorrection': {},
            'TopAccent': {},
            'ExtendedShapes': [],
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
        # pylint: disable=line-too-long
        top_accent.TopAccentAttachment, top_accent.TopAccentCoverage, top_accent.TopAccentAttachmentCount = \
            self._glyph_info('TopAccent')
        glyph_info = otTables.MathGlyphInfo()
        glyph_info.MathItalicsCorrectionInfo = italic_corr
        glyph_info.MathTopAccentAttachment = top_accent
        glyph_info.ExtendedShapeCoverage = self._coverage(self.glyph_info['ExtendedShapes'])
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
            self._variants('Horizontal')
        variants.VertGlyphConstruction, variants.VertGlyphCoverage, variants.VertGlyphCount = \
            self._variants('Vertical')
        return variants

    def _variants(self, name: str):
        constructions = {}
        for glyph, variants in self.variants[name + 'Variants'].items():
            constructions[glyph] = self._glyph_construction(variants)
        for glyph, component in self.variants[name + 'Components'].items():
            if glyph not in constructions:
                constructions[glyph] = self._glyph_construction({})
            constructions[glyph].GlyphAssembly = self._glyph_assembly(component)
        return constructions.values(), self._coverage(constructions.keys()), len(constructions)

    @staticmethod
    def _glyph_construction(variants: dict):
        construction = otTables.MathGlyphConstruction()
        construction.GlyphAssembly = None
        construction.VariantCount = len(variants)
        construction.MathGlyphVariantRecord = []
        for glyph, advance in variants.items():
            r = otTables.MathGlyphVariantRecord()
            r.VariantGlyph = glyph
            r.AdvanceMeasurement = advance
            construction.MathGlyphVariantRecord.append(r)
        return construction

    @staticmethod
    def _glyph_assembly(component: dict):
        t = otTables.GlyphAssembly()
        t.ItalicsCorrection = MathTable._math_value(component['italicsCorrection'])
        t.PartCount = len(component['parts'])
        t.PartRecords = []
        for part in component['parts']:
            r = otTables.GlyphPartRecord()
            r.glyph = part['name']
            r.StartConnectorLength = part['startConnector']
            r.EndConnectorLength = part['endConnector']
            r.FullAdvance = part['fullAdvance']
            r.PartFlags = 0x0001 if part['isExtender'] else 0xFFFE
            t.PartRecords.append(r)
        return t

    @staticmethod
    def _math_value(value):
        t = otTables.MathValueRecord()
        t.DeviceTable = None
        t.Value = value
        return t

    @staticmethod
    def _coverage(glyphs):
        c = otTables.Coverage()
        c.glyphs = glyphs
        return c


class MathTableInstantiator:

    def __init__(
        self,
        data: dict[str],
        interpolation: list[tuple[int, float]],
        removed_glyphs: list[str],
    ):
        self.master_constants:  dict[str, dict] = data['MathConstants']
        self.master_glyph_info: dict[str]       = data['MathGlyphInfo']
        self.master_variants:   dict[str]       = data['MathVariants']
        self.interpolation = interpolation
        if removed_glyphs:
            self.removed_glyphs = set(removed_glyphs)
        else:
            self.removed_glyphs = set()

    def generate(self) -> MathTable:
        math_table = MathTable()
        math_table.constants  = self._generate_constants()
        math_table.glyph_info = self._generate_glyph_info()
        math_table.variants   = self._generate_variants()
        return math_table

    def _generate_constants(self) -> dict[str, dict[str]]:
        return {
            name: {
                'value': self._generate(d['value']),
                'isMathValue': d['isMathValue'],
            }
            for name, d in self.master_constants.items()
        }

    def _generate(self, values: list[int]) -> int:
        '''Generate a specific value for the instance.'''
        return round(sum(values[i] * v for i, v in self.interpolation))

    def _generate_glyph_info(self) -> dict[str]:
        return {
            'ItalicCorrection': self._glyph_info('ItalicCorrection'),
            'TopAccent':        self._glyph_info('TopAccent'),
            'ExtendedShapes':   self.master_glyph_info['ExtendedShapes'],
        }

    def _glyph_info(self, name: str) -> dict[str]:
        # TODO: consider brace layers
        return {
            g: self._generate(values)
            for g, values in self.master_glyph_info[name].items() if g not in self.removed_glyphs
        }

    def _generate_variants(self) -> dict[str]:
        return {
            'MinConnectorOverlap':  self._generate(self.master_variants['MinConnectorOverlap']),
            'HorizontalVariants':   self._variants('Horizontal'),
            'VerticalVariants':     self._variants('Vertical'),
            'HorizontalComponents': self._components('Horizontal'),
            'VerticalComponents':   self._components('Vertical'),
        }

    def _variants(self, name: str) -> dict[str]:
        '''`name` can be either `"Horizontal"` or `"Vertical"`.'''
        return {
            glyph: {g: self._generate(values) for g, values in variants.items()}
            for glyph, variants in self.master_variants[name + 'Variants'].items()
        }

    def _components(self, name: str) -> dict[str]:
        '''`name` can be either `"Horizontal"` or `"Vertical"`.'''
        return {
            glyph: {
                # TODO: need to be interpolated
                'italicsCorrection': componet['italicsCorrection'],
                'parts': list(map(self._part, componet['parts'])),
            }
            for glyph, componet in self.master_variants[name + 'Components'].items()
        }

    def _part(self, part: dict[str]) -> dict[str]:
        return {
            'name':           part['name'],
            'isExtender':     part['isExtender'],
            'startConnector': self._generate(part['startConnector']),
            'endConnector':   self._generate(part['endConnector']),
            'fullAdvance':    self._generate(part['fullAdvance']),
        }
