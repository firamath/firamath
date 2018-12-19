#!/usr/bin/python
"""Analysis interpolation coefficients for different weights.
"""

from __future__ import print_function

import collections
import itertools
import json
import math
import os
import fontforge as ff


def _make_unicode_list(begin_index, end_index=None):
    _prefix_dict = {5: "u", 4: "uni", 3: "uni0", 2: "uni00"}
    if end_index is None:
        end_index = begin_index
    end_index += 1
    result = []
    for i in range(begin_index, end_index):
        unicode_hex_str = hex(i)[2:].upper()  # Remove `0x` and capitalize
        result.append(_prefix_dict[len(unicode_hex_str)] + unicode_hex_str)
    return result

# Some glyphs are excluded since the points in different weights may not correspond.
ANALYSIS_GLYPH_LIST = list(itertools.chain.from_iterable(
    _make_unicode_list(*x) for x in
    [(0x0021, 0x003F),      # Basic Latin (1)
     (0x0041, 0x0070),      # Basic Latin (2)
     (0x0072, 0x007E),      # Basic Latin (2)
     (0x0400, 0x042F),      # Cyrillic capital letters
     (0x210E, ),            # Italic h
     (0x2202, ),            # Partial
     (0x2205, ),            # Empty set
     (0x2206, ),            # Increment
     (0x221E, ),            # Infinity
     (0x1D434, 0x1D443),    # Mathematical italic latin letters (1)
     (0x1D45B, 0x1D467)]))  # Mathematical italic latin letters (2)

# DEBUG
# ANALYSIS_GLYPH_LIST = _make_unicode_list(0x30, 0x39)


def _open_font(weight):
    file_name = os.sep.join([os.getcwd(), "src", "FiraMath-" + weight + ".sfd"])
    return ff.open(file_name)


def _subdivide(min_val, max_val, n=10):
    return [min_val + float(max_val - min_val) / n * i for i in range(n + 1)]


def layer_distance(layer_a, layer_b):
    """Calculate distance between two layers.
    This is the average Euclidean distance between each points.
    """
    def _contour_distance(contour_a, contour_b):
        total_distance = 0.0
        for point_a, point_b in zip(contour_a, contour_b):
            x, y = point_a.x - point_b.x, point_a.y - point_b.y
            total_distance += math.sqrt(x**2 + y**2)
        return total_distance
    distance, point = 0.0, 0
    for contour_a, contour_b in zip(layer_a, layer_b):
        distance += _contour_distance(contour_a, contour_b)
        point += len(contour_a)
    return distance / point


def _list_min_pos(_list):
    min_pos = _list.index(min(_list))
    if min_pos == 0:
        interval_a, interval_b = min_pos, min_pos + 1
    elif min_pos == len(_list) - 1:
        interval_a, interval_b = min_pos - 1, min_pos
    elif _list[min_pos - 1] <= _list[min_pos + 1]:
        interval_a, interval_b = min_pos - 1, min_pos
    else:
        interval_a, interval_b = min_pos, min_pos + 1
    return {"min_pos": min_pos, "min_interval": (interval_a, interval_b)}


def get_interpolation_t(font_a, font_b, font_check, t_list):
    """Find the best interpolation coefficient `t` among `t_list`.

    Algorithm:
        - Interpolate between `font_a` and `font_b`, with all the `t` in `t_list`;
        - Calculate the distance between `font_check` the interpolated one;
        - Give the minimal `t`.
    """
    dist_list = []
    for t in t_list:
        dist_list_at_t = []
        for glyph_name in ANALYSIS_GLYPH_LIST:
            layer_a = font_a[glyph_name].layers[1]
            layer_b = font_b[glyph_name].layers[1]
            layer_check = font_check[glyph_name].layers[1]
            layer_inter = layer_a.interpolateNewLayer(layer_b, t)
            dist_list_at_t.append(layer_distance(layer_check, layer_inter))
        dist_list.append(sum(dist_list_at_t) / len(dist_list_at_t))
    return _list_min_pos(dist_list)


def analysis(weight_list, accuracy_goal=2):
    """Use iteration method to find the best interpolation coefficient.

    Args:
        - `weight_list`: the first one and the last one will be used as base style.
        - `accuracy_goal`: The decimals of the final results.
    """
    font_list = [_open_font(w) for w in weight_list]
    font_a, font_b = font_list[0], font_list[-1]
    result = collections.OrderedDict()
    for font_check in font_list:
        accuracy_count = 0
        t_interval = (0, 1)  # Initial interval
        while accuracy_count < accuracy_goal:
            t_list = _subdivide(*t_interval)
            t_dict = get_interpolation_t(font_a, font_b, font_check, t_list)
            t_interval = tuple(t_list[i] for i in t_dict["min_interval"])
            accuracy_count += 1
        result.update({font_check.weight: t_list[t_dict["min_pos"]]})
    return (weight_list[0] + "-" + weight_list[-1], result)


def _main():
    weight_lists = [
        ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular"],
        ["Regular", "Medium", "SemiBold", "Bold"],
        ["Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"],
        ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular", "Medium",
         "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]]
    accuracy_goal = 4
    result = collections.OrderedDict([analysis(w_list, accuracy_goal) for w_list in weight_lists])
    json.encoder.FLOAT_REPR = lambda o: format(o, "." + str(accuracy_goal) + "f")
    print(json.dumps(result, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    _main()
