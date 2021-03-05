'''OpenType MATH table for Fira Math.

Note that only *global* information are described here, while glyph-specific data such as
top accent position are stored in the `.glyphspackage` file.
'''

from collections import OrderedDict

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib.ttFont import newTable
from fontTools.ttLib.tables import otTables

def math_table(font, glyph_info):
    table = otTables.MATH()
    table.Version = 0x00010000
    table.MathConstants = math_constants()
    table.MathGlyphInfo = math_glyph_info(glyph_info)
    table.MathVariants = math_variants(font)
    wrapper = newTable('MATH')
    wrapper.table = table
    return wrapper

def _math_value(value):
    t = otTables.MathValueRecord()
    t.DeviceTable = None
    t.Value = value
    return t

def _coverage(glyphs):
    coverage = otTables.Coverage()
    coverage.glyphs = glyphs
    return coverage

def math_constants():
    constants = otTables.MathConstants()

    # Global
    constants.ScriptPercentScaleDown = 72
    constants.ScriptScriptPercentScaleDown = 58
    constants.DelimitedSubFormulaMinHeight = 1500
    constants.DisplayOperatorMinHeight = 1500
    constants.MathLeading = _math_value(150)
    constants.AxisHeight = _math_value(280)
    constants.AccentBaseHeight = _math_value(527)
    constants.FlattenedAccentBaseHeight = _math_value(689)

    # Subscript and superscript
    constants.SubscriptShiftDown = _math_value(350)
    constants.SubscriptTopMax = _math_value(527)
    constants.SubscriptBaselineDropMin = _math_value(250)
    constants.SuperscriptShiftUp = _math_value(400)
    constants.SuperscriptShiftUpCramped = _math_value(270)
    constants.SuperscriptBottomMin = _math_value(130)
    constants.SuperscriptBaselineDropMax = _math_value(360)
    constants.SubSuperscriptGapMin = _math_value(200)
    constants.SuperscriptBottomMaxWithSubscript = _math_value(527)
    constants.SpaceAfterScript = _math_value(41)

    # Upper and lower limit
    constants.UpperLimitGapMin = _math_value(150)
    constants.UpperLimitBaselineRiseMin = _math_value(150)
    constants.LowerLimitGapMin = _math_value(150)
    constants.LowerLimitBaselineDropMin = _math_value(600)

    # Stack
    constants.StackTopShiftUp = _math_value(450)
    constants.StackTopDisplayStyleShiftUp = _math_value(580)
    constants.StackBottomShiftDown = _math_value(480)
    constants.StackBottomDisplayStyleShiftDown = _math_value(700)
    constants.StackGapMin = _math_value(200)
    constants.StackDisplayStyleGapMin = _math_value(500)

    # Stretch stack
    constants.StretchStackTopShiftUp = _math_value(300)
    constants.StretchStackBottomShiftDown = _math_value(600)
    constants.StretchStackGapAboveMin = _math_value(150)
    constants.StretchStackGapBelowMin = _math_value(150)

    # Fraction
    constants.FractionNumeratorShiftUp = _math_value(450)
    constants.FractionNumeratorDisplayStyleShiftUp = _math_value(580)
    constants.FractionDenominatorShiftDown = _math_value(480)
    constants.FractionDenominatorDisplayStyleShiftDown = _math_value(700)
    constants.FractionNumeratorGapMin = _math_value(80)
    constants.FractionNumDisplayStyleGapMin = _math_value(200)
    constants.FractionRuleThickness = _math_value(76)
    constants.FractionDenominatorGapMin = _math_value(80)
    constants.FractionDenomDisplayStyleGapMin = _math_value(200)

    # Skewed fraction
    constants.SkewedFractionHorizontalGap = _math_value(0)
    constants.SkewedFractionVerticalGap = _math_value(0)

    # Overbar and underbar
    constants.OverbarVerticalGap = _math_value(150)
    constants.OverbarRuleThickness = _math_value(66)
    constants.OverbarExtraAscender = _math_value(50)
    constants.UnderbarVerticalGap = _math_value(150)
    constants.UnderbarRuleThickness = _math_value(66)
    constants.UnderbarExtraDescender = _math_value(50)

    # Radical
    constants.RadicalVerticalGap = _math_value(96)
    constants.RadicalDisplayStyleVerticalGap = _math_value(142)
    constants.RadicalRuleThickness = _math_value(76)
    constants.RadicalExtraAscender = _math_value(76)
    constants.RadicalKernBeforeDegree = _math_value(276)
    constants.RadicalKernAfterDegree = _math_value(-400)
    constants.RadicalDegreeBottomRaisePercent = 64

    return constants

def math_glyph_info(glyph_info_dict):
    glyph_info = otTables.MathGlyphInfo()

    # TODO:
    glyph_info.MathItalicsCorrectionInfo = None

    # Top accents
    top_accent_dict = glyph_info_dict['MathTopAccentAttachment']
    glyph_info.MathTopAccentAttachment = otTables.MathTopAccentAttachment()
    glyph_info.MathTopAccentAttachment.TopAccentAttachment = [
        _math_value(value) for value in top_accent_dict.values()
    ]
    glyph_info.MathTopAccentAttachment.TopAccentCoverage = _coverage(top_accent_dict.keys())
    glyph_info.MathTopAccentAttachment.TopAccentAttachmentCount = len(top_accent_dict)

    # TODO:
    glyph_info.ExtendedShapeCoverage = None

    # TODO:
    glyph_info.MathKernInfo = None

    return glyph_info

def math_variants(font):
    variants = otTables.MathVariants()

    variants.MinConnectorOverlap = 20

    # TODO: horizontal part
    variants.HorizGlyphConstruction = []
    variants.HorizGlyphCoverage = None
    variants.HorizGlyphCount = 0

    vert_variant_glyphs_a = [
        'integral',
        'dblintegral',
        'tripleintegral',
        'quadrupleIntegralOperator',
        'contourintegral',
        'surfaceintegral',
        'volumeintegral',
        'product',
        'coproduct',
        'summation',
        'summationWithIntegral',
        'nAryCircledDotOperator',
        'nAryCircledPlusOperator',
        'nAryCircledTimesOperator',
    ]
    vert_variant_glyphs_b = [
        'parenleft',
        'parenright',
        'bracketleft',
        'bracketright',
        'braceleft',
        'braceright',
        'leftanglebracket-math',
        'leftdoubleanglebracket-math',
        'rightanglebracket-math',
        'rightdoubleanglebracket-math',
        'leftflattenedparenthesis-math',
        'rightflattenedparenthesis-math',
        'leftCeiling',
        'leftFloor',
        'rightCeiling',
        'rightFloor',
        'bar',
        'dblverticalbar',
        'tripleVerticalBarDelimiter',
        'radical',
        'cuberoot',
        'fourthroot',
    ]

    vert_variants = OrderedDict()
    for g in vert_variant_glyphs_a:
        vert_variants[g] = ['{}.size01'.format(g)]
    for g in vert_variant_glyphs_b:
        vert_variants[g] = ['{}.size{:02}'.format(g, i) for i in range(1, 16)]

    variants.VertGlyphConstruction = [
        _glyph_construction(font, g, vars, 'vert') for g, vars in vert_variants.items()
    ]
    variants.VertGlyphCoverage = _coverage(vert_variants.keys())
    variants.VertGlyphCount = len(vert_variants)

    return variants

def _glyph_construction(font, glyph, variants, direction):
    t = otTables.MathGlyphConstruction()
    t.GlyphAssembly = None
    t.VariantCount = len(variants) + 1
    t.MathGlyphVariantRecord = []
    for g in [glyph] + variants:
        r = otTables.MathGlyphVariantRecord()
        r.AdvanceMeasurement = _advance_measurement(font, g, direction)
        r.VariantGlyph = g
        t.MathGlyphVariantRecord.append(r)
    return t

def _advance_measurement(font, glyph, direction):
    bbox = _bounding_box(font, glyph)
    if direction == 'horiz':
        return bbox[2] - bbox[0] + 1
    if direction == 'vert':
        return bbox[3] - bbox[1] + 1

def _bounding_box(font, glyph):
    '''Return the bounding box of `glyph`, which is a 4-tuple: `(xMin, yMin, xMax, yMax)`.'''
    glyph_set = font.getGlyphSet()
    pen = BoundsPen(glyph_set)
    glyph_set[glyph].draw(pen)
    return pen.bounds
