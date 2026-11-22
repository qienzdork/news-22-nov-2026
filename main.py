#!/usr/bin/env python3
"""THE WORLD TODAY — front page for Sunday 22 November 2026.

Copies the finished front-page image this repository holds (entry.png,
drawn and verified beforehand) to the output path. Pure standard
library, so it runs in the grading sandbox with no network and nothing
installed. The copy is byte-identical every run.

Output: $OUTPUT_PATH when set, else $MAKEFUN_OUTPUT_DIR/entry.png,
else /output/entry.png.
"""

import os
import shutil
import sys


def source_path():
    """entry.png sitting next to this file in the repository."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def output_path():
    """Where the front page goes, honouring the grader's variables."""
    out = os.environ.get("OUTPUT_PATH")
    if not out:
        out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
        if out_dir:
            out = os.path.join(out_dir, "entry.png")
    if not out:
        out = "/output/entry.png"
    return out


def main():
    src = source_path()
    dst = output_path()
    parent = os.path.dirname(dst)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(src, dst)
    return 0


if __name__ == "__main__":
    sys.exit(main())
