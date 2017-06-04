#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import glob


def eprint(*args, **kwargs):
    # https://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)


def aggregate(path):
    for filepath in glob.glob(os.path.join(path, "*")):
        filename = os.path.basename(filepath)
        if '-' not in filename:
            eprint("File name %s not well-formed; ignoring..." % filename)
            continue

        website, _ = filename.split("-", 1)
        with open(filepath, "r") as f:
            print("%s,%s" % (website, f.read().strip()))


if __name__ == "__main__":
    aggregate(sys.argv[1])
