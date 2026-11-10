#!/usr/bin/env python3
"""Sanity-check a generated `stockfont_data.rs`.

The firmware binary-searches the entry table (`Font::glyph`), so the entries
*must* be in ascending code order or the glyph silently disappears; and each
entry's blob offset must leave room for w*ih bits inside `_B`, otherwise the
glyph draws as blanks. Neither shows up at build time.

    check_fontdata.py --file firmware/src/stockfont_data.rs [--font TEXT22]
"""

import argparse
import io
import re
import sys

ENTRY = re.compile(r"E\((0x[0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(\d+),(\d+)\)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--font", default="TEXT22")
    a = p.parse_args()

    text = io.open(a.file, encoding="utf-8").read()
    e = re.search(r"pub static %s_E: \[Entry; \d+\] = \[(.*?)\];" % a.font, text, re.S)
    if not e:
        sys.exit("no %s_E" % a.font)
    rows = [(int(m.group(1), 16), int(m.group(2)), int(m.group(3)), int(m.group(4)),
             int(m.group(5)), int(m.group(6)), int(m.group(7)), int(m.group(8)))
            for m in ENTRY.finditer(e.group(1))]
    b = re.search(r"pub static %s_B: \[u8; (\d+)\]" % a.font, text)
    blob_len = int(b.group(1))

    problems = []
    codes = [r[0] for r in rows]
    if codes != sorted(codes):
        problems.append("entries are not sorted by code (binary search would miss glyphs)")
    if len(set(codes)) != len(codes):
        problems.append("duplicate codes")
    for code, off, w, h, adv, yoff, t, ih in rows:
        need = (w * ih + 7) // 8
        if off + need > blob_len:
            problems.append("U+%04X: blob %d+%d > %d" % (code, off, need, blob_len))
        if t + ih > h:
            problems.append("U+%04X: ink rows %d..%d outside h=%d" % (code, t, t + ih, h))

    cjk = sum(1 for c in codes if c >= 0x3000)
    print("%s: %d entries (%d hanzi), blob %d bytes, %d..%d" %
          (a.font, len(rows), cjk, blob_len,
           min(codes) if codes else 0, max(codes) if codes else 0))
    for m in problems[:10]:
        print("   PROBLEM %s" % m)
    print("ok" if not problems else "%d problem(s)" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
