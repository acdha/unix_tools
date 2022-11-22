#!/usr/bin/env python3
"""Convert UTF-8 text files to Unicode normalization form NFC

Converts stdin or a list of filenames on the command-line. Files will be edited
*IN PLACE*
"""

import fileinput
import unicodedata

for line in fileinput.input(inplace="1", backup=".bak"):
    u_line = line.decode("utf-8")
    print(unicodedata.normalize("NFC", u_line).encode("utf-8"), end="")
