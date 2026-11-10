#!/usr/bin/env python3
"""Revert the five least visible translations to pay for the rest.

Measured with the region B floor temporarily lowered: the image was 644 B
short. One hanzi costs about 64 B in region B, so ten have to go. Chosen so
each affected screen still reads as one language:

  BOX_NAME  "有效 100ms" / "峰值"   -> English   the inrush page's two value
                                              boxes; the numbers dominate
  gallery   "无数据"               -> "No data"  only shows on an empty card
  功率计接线                        -> "Power meter: wiring"  a dialog title
  REC_INTERVALS  "最快"            -> "Fast"     one value on the record page
  REC_DURATIONS  "手动停"          -> "手停"      same row, one character less

Everything else from mkpatch9 stays.

    python mkpatch11.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui_inrush.rs": [
        ('const BOX_NAME: [&str; 2] = ["\u6709\u6548 100ms", "\u5cf0\u503c"];',
         'const BOX_NAME: [&str; 2] = ["Irms 100 ms", "Peak"];'),
    ],
    "gallery.rs": [
        ('rect(px, py, pw, ph), "\u65e0\u6570\u636e"', 'rect(px, py, pw, ph), "No data"'),
    ],
    "ui_power.rs": [
        ('"\u529f\u7387\u8ba1\u63a5\u7ebf"', '"Power meter: wiring"'),
    ],
    "ui.rs": [
        ('"\u6700\u5feb"];', '"Fast"];'),
        ('"\u624b\u52a8\u505c"', '"\u624b\u505c"'),
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
        sys.stderr.write("%-14s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
