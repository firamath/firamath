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
