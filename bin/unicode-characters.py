#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, unicode_literals

from unicodedata import category, name
from binascii import hexlify
import fileinput
import re
import sys

MAJOR_VERSION = sys.version_info[0]

CACHE = {}

print("%8s\t%8s\t%s\t%s" % ("Char", "UTF8 Hex", "Category", "Name"))
print("-" * 72)

for line in fileinput.input():
    if MAJOR_VERSION < 3:
        line = line.decode("utf-8")
    for char in line:
        try:
            cat, display_char, utf8_hex = CACHE[char]
        except KeyError:
            cat = category(char)
            display_char = char.encode("unicode_escape").decode("ascii")
            utf8_hex = hexlify(char.encode("utf8")).decode("ascii")
            CACHE[char] = cat, display_char, utf8_hex

        print(display_char, utf8_hex, cat, name(char, "<UNKNOWN>"), sep="\t")
