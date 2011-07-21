#!/usr/bin/env python
"""Convert UTF-8 text files to Unicode normalization form NFC

Converts stdin or a list of filenames on the command-line. Files will be edited
*IN PLACE*
"""

import sys
import unicodedata
import fileinput


for line in fileinput.input(inplace="1", backup=".bak"):
    u_line = line.decode("utf-8")
    # Note trailing comma to avoid adding extra newlines:
    print unicodedata.normalize('NFC', u_line).encode("utf-8"),
