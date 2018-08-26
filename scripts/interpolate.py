#!/usr/bin/python

import os
import platform
import re

CWD = os.getcwd()
if platform.system() == "Linux":
    PATH = CWD + "/temp/sfd/braces.sfdir/"
elif platform.system() == "Windows":
    PATH = CWD + "\\temp\\sfd\\braces.sfdir\\"

def get_points(path):
    """
    Return:
        2-dimensional tensor of points.
        - 1st dimension: splines
        - 2nd dimension: points:
            (list of points' coordinates, type, tag)
    """
    with open(path) as f:
        f_str = f.read()
        width = int(re.findall(r"Width: (\S+)\n", f_str)[0])
        spline_set_str = re.findall(
            r"SplineSet\n(.+)EndSplineSet", f_str, flags=re.DOTALL)[0]

    spline_set_list = re.findall(
        r" ?(.+ )([clm]) (.+)\n",  # $1=points list, $2=type, $3=tag
        spline_set_str)
    index = -1
    points_list = []
    for i in spline_set_list:
        if i[1] == "m":
            index += 1
            points_list.append([])
        points_list[index].append({"points": [int(x) for x in i[0].split()],
                                   "type": i[1],
                                   "tag": i[2]})
    return width, points_list

def list_subdivide(list_min, list_max, n, round_to_int=True):
    """Return `n` subdivisions of two equal-length lists.

    Note that the result will be a list of `n+1` elements.
    """
    if round_to_int:
        subdivide = lambda a, b, i: (b - a) * i // n + a
    else:
        subdivide = lambda a, b, i: (b - a) * i / n + a
    result = []
    for i in range(n + 1):
        result.append([subdivide(min_val, max_val, i)
                       for min_val, max_val in zip(list_min, list_max)])
    return result

def get_spline_set_str(points):
    """Return a string of SplineSet.
    """
    spline_set_str = ""
    for i in points:
        if i["type"] == "m":
            point_str = ""
            for coord in i["points"]:
                point_str += str(coord) + " "
        else:
            point_str = " "
            for coord in i["points"]:
                point_str += str(coord) + " "
        spline_set_str += point_str + i["type"] + " " + i["tag"] + "\n"
    return spline_set_str

def interpolate(glyph_min, glyph_max, num):
    result = []
    for spline_min, spline_max in zip(glyph_min, glyph_max):
        for point_min, point_max in zip(spline_min, spline_max):
            if point_min["type"] == point_max["type"]:
                points_list = list_subdivide(
                    point_min["points"], point_max["points"], num)
                temp = []
                for i in points_list:
                    temp.append({"points": i,
                                 "type": point_min["type"],
                                 "tag": point_min["tag"]})
            else:
                print("WARNING!")
            result.append(temp)
    # Transpose `result`
    return map(list, zip(*result))

def get_new_meta_data(start_name, num):
    start_unicode_dec = int(start_name[3:], 16) + 1

    # Count the files in `PATH`. For glyph's index.
    _, _, files = next(os.walk(PATH))
    glyphs_count = len(files) - 1  # Subtract `font.props`

    result = []
    for i in range(num):
        unicode_dec = start_unicode_dec + i
        unicode_hex = hex(unicode_dec)[2:].upper()
        result.append({"name": "uni" + unicode_hex,
                       "encoding": str(unicode_dec),
                       "index": str(glyphs_count + i)})
    return result

def generate_new_glyphs(min_name, max_name, start_name, num):
    path_min = PATH + min_name + ".glyph"
    path_max = PATH + max_name + ".glyph"
    width_min, glyph_min = get_points(path_min)
    width_max, glyph_max = get_points(path_max)
    with open(path_min) as f:
        old_str = f.read()

    spline_set_list = interpolate(glyph_min, glyph_max, num)
    width_list = [str(x[0]) for x in list_subdivide([width_min], [width_max], num)]
    encoding_name_list = get_new_meta_data(start_name, num + 1)

    result = []
    for spline_set, width, encoding_name in zip(
            spline_set_list, width_list, encoding_name_list):
        replace_spline_set = lambda match_obj: \
            match_obj.group(1) + width + \
            match_obj.group(3) + \
            match_obj.group(4) + get_spline_set_str(spline_set) + match_obj.group(6)
        replace_encoding = lambda match_obj: \
            match_obj.group(1) + encoding_name["name"] + \
            match_obj.group(3) + encoding_name["encoding"] + " " + \
                                 encoding_name["encoding"] + " " + \
                                 encoding_name["index"] + "\n"
        new_str = re.sub(
            #  1        2    3   4            5   6
            r"(Width: )(\S+)(.+)(SplineSet\n)(.+)(EndSplineSet)",
            replace_spline_set,
            old_str,
            flags=re.DOTALL)
        new_str = re.sub(
            #  1            2   3             4     5     6
            r"(StartChar: )(.+)(\nEncoding: )(\S+) (\S+) (\S+)\n",
            replace_encoding,
            new_str)
        file_name = encoding_name["name"] + ".glyph"
        result.append({"name": file_name, "content": new_str})
    return result

def write_files(file_list):
    for i in file_list:
        if platform.system() == "Linux":
            with open(PATH + i["name"], "w") as file_i:
                file_i.write(i["content"])
        elif platform.system() == "Windows":
            with open(PATH + i["name"], "w", newline="\n") as file_i:
                file_i.write(i["content"])

def main():
    write_files(generate_new_glyphs("uniE000", "uniE015", "uniE100", 15))
    write_files(generate_new_glyphs("uniE001", "uniE016", "uniE200", 15))

if __name__ == "__main__":
    main()
