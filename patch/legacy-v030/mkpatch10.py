#!/usr/bin/env python3
"""Trim three translations so the image fits.

Region B is still short after cutting the help pages, and a hanzi costs about
54 B. These are the least valuable of the batch:

  BOX_NAME "有效值100ms" -> "有效 100ms"   the 值 is obvious from context
  the touch-test legend "校正" / "下滑" back to "corrected" / "down"
      -- those two sit next to live coordinate readouts that are English
      anyway (x'= / y'=), so the legend reads fine in English

    python mkpatch10.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui_inrush.rs": [
        ('"\u6709\u6548\u503c100ms"', '"\u6709\u6548 100ms"'),
    ],
    "ui_touchtest.rs": [
        ('rect(LINE_X + 74, LEGEND_Y, 100, 20), "\u6821\u6b63"',
         'rect(LINE_X + 74, LEGEND_Y, 100, 20), "corrected"'),
        ('rect(LINE_X + 203, LEGEND_Y, 60, 20), "\u4e0b\u6ed1"',
         'rect(LINE_X + 203, LEGEND_Y, 60, 20), "down"'),
    ],
}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            n = text.count(old)
            if n != 1:
                sys.exit("%s: %d occurrences of %r" % (name, n, old[:50]))
            text = text.replace(old, new)
            total += 1
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-16s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
