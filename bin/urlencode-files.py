#!/usr/bin/env python3

from urllib.parse import quote
import sys

for filename in sys.argv[1:]:
    print(filename)
    with open(filename, "r", encoding="utf-8") as f:
        print(quote(f.read()))
    print()
