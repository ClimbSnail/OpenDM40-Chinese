#!/usr/bin/env python3
"""Flag Chinese strings drawn with a font that has no hanzi.

Only TEXT22 carries the 343 hanzi glyphs this project adds; every other font
(ASCII26, SC_F16, F14, F78, ...) is the stock table and has no CJK at all, so
a Chinese literal drawn with one of them comes out blank (or as boxes) on the
panel -- and nothing in the build complains, because it is still valid UTF-8.

    check_fonts.py --src firmware/src [--font TEXT22]

Heuristic, line based: a line with a CJK string literal must mention the one
font that can draw it. Wrapped `sf::label(font, rect(\n ... "中文" ...))` calls
span lines, so a few false positives are expected; each hit names the file and
line so it can be eyeballed.
"""

import argparse
import io
import os
import re
import sys

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
# Fonts that render a `&str` through `stockfont`'s table lookup.
FONTS = r"(?:ASCII26|TEXT22|SC_F16|SC_F20|F14|F78|UNIT|LETTERS|K_FONT|ASCII12|ASCII26)"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--font", default="TEXT22")
    a = p.parse_args()

    bad = 0
    for dirpath, _, files in os.walk(a.src):
        for f in sorted(files):
            if not f.endswith(".rs"):
                continue
            path = os.path.join(dirpath, f)
            for ln, line in enumerate(io.open(path, encoding="utf-8", errors="replace"), 1):
                if line.lstrip().startswith("//"):
                    continue
                if not CJK.search(line):
                    continue
                fonts = {m.group(1) for m in re.finditer(r"\b(" + FONTS + r")\b", line)}
                if a.font in fonts or not fonts:
                    continue
                bad += 1
                print("%s:%d  drawn with %s\n    %s" % (f, ln, ",".join(sorted(fonts)), line.strip()[:110]))
    print("---\nlines with CJK on a font without hanzi: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
