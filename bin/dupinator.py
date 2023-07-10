#! /usr/bin/env python3
"""
Scan the provided directories on the command-line and report duplicate files, optionally removing them
"""

import argparse
import hashlib
import os
import shutil
from binascii import hexlify
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm


def find_files(directories):
    for directory in directories:
        walker = os.walk(directory, followlinks=True)
        for dirpath, dirnames, filenames in walker:
            for filename in filenames:
                yield os.path.join(dirpath, filename)


def get_file_hash(filename):
    if not os.path.isfile(filename):
        raise ValueError("Expected %s to be a normal file" % filename)

    h = hashlib.sha512()

    with open(filename, "rb") as f:
        while True:
            d = f.read(1024 * 1024)

            if d:
                h.update(d)
            else:
                break

    return filename, h.digest()


def find_duplicates(directories):
    for d in directories:
        if not os.path.exists(d):
            raise ValueError("Directory %s does not exist" % d)
        elif not os.path.isdir(d):
            raise ValueError("Expected %s to be a directory" % d)

    file_hashes = defaultdict(set)

    print("Scanning for files…")

    all_files = deque()
    for filename in tqdm(find_files(directories)):
        all_files.append(filename)

    print("Hashing %d files" % len(all_files))

    with ThreadPoolExecutor() as executor:
        for filename, digest in tqdm(
            executor.map(get_file_hash, all_files), total=len(all_files)
        ):
            file_hashes[digest].add(filename)

    for digest, filenames in file_hashes.items():
        if len(filenames) < 2:
            continue
        else:
            yield digest, filenames


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip())

    dupe_mode = parser.add_mutually_exclusive_group()

    dupe_mode.add_argument(
        "--report", action="store_true", default=True, help="Report duplicates"
    )
    dupe_mode.add_argument(
        "--trash",
        action="store_true",
        default=False,
        help="Move duplicates to the Trash",
    )
    dupe_mode.add_argument(
        "--delete", action="store_true", default=False, help="Delete files"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Display progress information",
    )
    parser.add_argument("directories", nargs="+")

    args = parser.parse_args()

    trash_dir = os.path.expanduser("~/.Trash/")
    if args.trash and not os.path.isdir(trash_dir):
        raise RuntimeError(
            "Expected to move duplicates to non-existent %s!" % trash_dir
        )

    for digest, filenames in find_duplicates(args.directories):
        # filenames = sorted(filenames, key=os.path.getmtime)
        filenames = sorted(filenames, key=lambda i: "iTunes Media" not in i)

        print(hexlify(digest).decode("ascii"))
        print("\tOriginal: %s" % filenames[0])

        for f in filenames[1:]:
            if args.delete:
                print("\tDeleting: %s" % f)
                os.remove(f)
            elif args.trash:
                print("\tTrashing: %s" % f)
                shutil.move(f, os.path.join(trash_dir, os.path.basename(f)))
            else:
                print("\tDuplicate: %s" % f)

        print()


if __name__ == "__main__":
    main()
