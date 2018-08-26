#!/usr/bin/python

import os
import platform
import re

CWD = os.getcwd()

def write_files(file_list, content_list):
    """Write files in `file_list` with the content in `content_list`.
    """
    for i, content in zip(file_list, content_list):
        if platform.system() == "Linux":
            with open(i, "w") as file_i:
                file_i.write(content)
        elif platform.system() == "Windows":
            with open(i, "w", newline="\n") as file_i:
                file_i.write(content)

def delete_files(file_list):
    """Delete all files in `file_list`.
    """
    for i in file_list:
        os.remove(i)

def main():
    path = CWD + "/src/fira-math-regular.sfdir/"

    old_file_name_prefix = "_Name_Me."
    old_begin_index = 1654
    old_end_index = 1668

    new_file_name_prefix = "uni005D.size"
    new_glyph_name_prefix = new_file_name_prefix
    new_begin_index = 1

    old_file_name_list = []
    old_file_content_list = []
    new_file_name_list = []
    new_glyph_name_list = []
    for i in range(old_begin_index, old_end_index + 1):
        file_name = path + old_file_name_prefix + str(i) + ".glyph"
        old_file_name_list.append(file_name)
        with open(file_name, "r") as f:
            old_file_content_list.append(f.read())
        new_glyph_index = str(i - old_begin_index + new_begin_index)
        new_file_name_list.append(
            path + new_file_name_prefix + new_glyph_index + ".glyph")
        new_glyph_name_list.append(new_glyph_name_prefix + new_glyph_index)

    new_file_content_list = []
    for i, j in zip(old_file_content_list, new_glyph_name_list):
        new_file_content_list.append(
            re.sub(r"(StartChar: )(.+)\n", r"\1" + j + r"\n", i))

    delete_files(old_file_name_list)
    write_files(new_file_name_list, new_file_content_list)

if __name__ == "__main__":
    main()
