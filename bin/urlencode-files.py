#!/usr/bin/env python3

import sys
from urllib.parse import quote

for filename in sys.argv[1:]:
    print(filename)
    with open(filename, encoding="utf-8") as f:
        print(quote(f.read()))
    print()
