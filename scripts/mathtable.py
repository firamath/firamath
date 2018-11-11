#!/usr/bin/python
"""Modify OpenType MATH table for Fira Math.

See https://docs.microsoft.com/typography/opentype/spec/math#mathconstants-table.
"""

import collections
import csv
import io
import os
import re


CWD = os.getcwd()
SFD_PATH = os.sep.join([CWD, "src"])
CSV_FILE_NAME = os.sep.join([CWD, "data", "math-constants.csv"])

FONT_FAMILY_NAME = "FiraMath"
WEIGHT_LIST = ["Thin", "UltraLight", "ExtraLight", "Light", "Book", "Regular",
               "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy", "Ultra"]

CSV_WEIGHTS_TUPLE = ("<Thin>", "<Regular>", "<Ultra>")

MATH_TABLE_PATTERN = re.compile(r"MATH:.+(Encoding: UnicodeFull\n)", flags=re.DOTALL)
MATH_TABLE_END_PATTERN = re.compile(r"(Encoding: UnicodeFull\n)")

MATH_CONSTANTS_INT_KEYS = [
    "ScriptPercentScaleDown",
    "ScriptScriptPercentScaleDown",
    "DelimitedSubFormulaMinHeight",
    "DisplayOperatorMinHeight",
    "RadicalDegreeBottomRaisePercent",
    "MinConnectorOverlap"
]


def sfd_read(sfd_file_name):
    with open(sfd_file_name, "r") as sfd_file:
        return sfd_file.read()


def sfd_write(sfd_file_name, sfd_str, backup=False):
    """Write `sfd_str` into SFD file.
    """
    def _write(file_name, content):
        with io.open(file_name, "w", newline="\n") as sfd_file:
            sfd_file.write(content)
    if backup:
        with open(sfd_file_name, "r") as sfd_file:
            bak_sfd_str = sfd_file.read()
        _write(sfd_file_name + ".bak", bak_sfd_str)
    _write(sfd_file_name, sfd_str)


def math_constants_interpolation(v1, v2, v3):
    """TODO: this is just a prototype.
    """
    def _interpolation(_v1, _v2, n):
        return tuple(((n - i) * _v1 + i * _v2) // n for i in range(n))
    part_1 = _interpolation(v1, v2, 5)  # There are 5 weights in [Thin..Regular].
    part_2 = _interpolation(v2, v3, 6)  # There are 6 weights in [Regular..Ultra].
    return part_1 + part_2 + (v3, )


def get_math_table(csv_file_name):
    def _read_row(row):
        _v2 = row["<Regular>"]
        _v1 = row["<Thin>"] if row["<Thin>"] != "" else _v2
        _v3 = row["<Ultra>"] if row["<Ultra>"] != "" else _v2
        return (row["<Name>"], math_constants_interpolation(int(_v1), int(_v2), int(_v3)))
    with open(csv_file_name, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        result = collections.OrderedDict([_read_row(row) for row in csv_reader])
        return result


def get_math_table_str(math_table, index):
    def _add_space(key):
        return " " if key not in MATH_CONSTANTS_INT_KEYS else ""
    math_table_entries = [
        "MATH:" + key + ": " + str(value[index]) + _add_space(key)
        for key, value in math_table.items()]
    return "\n".join(math_table_entries)


def add_math_table(sfd_file_name, math_table_str):
    sfd_str = re.sub(MATH_TABLE_PATTERN, r"\1", sfd_read(sfd_file_name))
    sfd_str = re.sub(MATH_TABLE_END_PATTERN, math_table_str + r"\n\1", sfd_str)
    sfd_write(sfd_file_name, sfd_str)


def _main():
    math_table = get_math_table(CSV_FILE_NAME)
    for i, weight in enumerate(WEIGHT_LIST):
        file_name = os.sep.join([SFD_PATH, FONT_FAMILY_NAME + "-" + weight + ".sfd"])
        add_math_table(file_name, get_math_table_str(math_table, i))


if __name__ == "__main__":
    _main()
    # [print(i, v) for i, v in get_math_table(CSV_FILE_NAME).items()]
    # print(math_constants_interpolation(10, 20, 30))
