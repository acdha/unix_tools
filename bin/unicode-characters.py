#!/usr/bin/env python
# encoding: utf-8

import fileinput
import unicodedata
import re

print u"%8s\t%8s\t%s\t%s" % ("Char", "UTF8 Hex", "Category", "Name")
print "-" * 72

for line in fileinput.input():
    for char in line.decode("utf-8"):
        category = unicodedata.category(char)
        display_char = char.encode("unicode_escape")
        utf8_hex = char.encode("utf8").encode("hex_codec")

        print u"%8s\t%8s\t%8s\t%s" % (display_char, utf8_hex, category,
                                    unicodedata.name(char, "<UNKNOWN>"))
