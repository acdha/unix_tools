#!/usr/bin/env python
# encoding: utf-8
from __future__ import print_function, unicode_literals

from unicodedata import category, name, normalize
from binascii import hexlify
import fileinput
import os
import sys

MAJOR_VERSION = sys.version_info[0]

CACHE = {}


# This is a bit gnarly but what we're trying to do is avoid a *MASSIVE* penalty
# endlessly encoding and reencoding Unicode strings for output. This is
# complicated by the fact that Python 2.x does not perform output encoding
# automatically when piped so we end up needing to re-open the file-handle so
# we can portably guarantee that our "stdout" object will be a simple file
# to which we can directly write byte-strings. This requires us to carefully
# encode output but that's worth a 500% boost on Python 3…
if MAJOR_VERSION < 3:
    stdout = os.fdopen(sys.stdout.fileno(), 'wb', 65536)
else:
    stdout = sys.stdout.buffer


def main():
    stdout.write(("%8s\t%8s\t%s\t%s\n" % ("Char", "UTF8 Hex", "Category",
                                          "Name")).encode("utf-8"))
    stdout.write(b"-" * 72)
    stdout.write(b"\n")
    stdout.flush()

    for line in fileinput.input():
        if MAJOR_VERSION < 3:
            line = line.decode("utf-8")

        for char in normalize("NFKC", line):
            # Since a given character can occur many times in our input, we'll
            # precompute everything including the concatenation and UTF-8
            # encoding:
            try:
                l = CACHE[char]
            except KeyError:
                cat = category(char).encode("utf-8")
                utf8_hex = hexlify(char.encode("utf8"))
                char_name = name(char, "<UNKNOWN>").encode("utf-8")
                CACHE[char] = l = char.encode("utf-8") + b"\t" + utf8_hex \
                                  + b"\t" + cat + b"\t" + char_name + b"\n"

            stdout.write(l)

if __name__ == "__main__":
    main()
