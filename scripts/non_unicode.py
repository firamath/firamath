"""Get the non-unicode glyphs from `non-unicode.toml`.
"""

import os
import toml


DATA_PATH = os.sep.join([os.getcwd(), "data"])
NON_UNICODE_TOML_FILE_NAME = os.sep.join([DATA_PATH, "non-unicode.toml"])


def get_non_unicode():
    """Return a list of tuples, each contains a non-unicode type and some glyphs.
    """
    parsed_toml = toml.load(NON_UNICODE_TOML_FILE_NAME)
    return [{"type": i["type"], "glyphs": _parse_glyph_list(i)}
            for i in parsed_toml["non-unicode"]]


def _parse_glyph_list(item: dict):
    """Return a list of non-unicode glyphs.
    """
    if "glyphs" in item:
        return item["glyphs"]
    if "base-glyphs" in item:
        if "suffixes" in item:
            result = []
            for suffix in item["suffixes"]:
                result += [glyph + "." + suffix for glyph in item["base-glyphs"]]
            return result
        if "suffix-base" in item and "suffix-range" in item:
            result = []
            if item["primary-index"] == "glyphs":
                for glyph in item["base-glyphs"]:
                    result += [glyph + "." + item["suffix-base"] + str(i + 1)
                               for i in range(item["suffix-range"])]
                return result
            if item["primary-index"] == "suffixes":
                for i in range(item["suffix-range"]):
                    result += [glyph + "." + item["suffix-base"] + str(i + 1)
                               for glyph in item["base-glyphs"]]
                return result
            print("WARNING!")
            return []
    print("WARNING!")
    return []


def _main():
    for i in get_non_unicode():
        print(i)


if __name__ == "__main__":
    _main()
