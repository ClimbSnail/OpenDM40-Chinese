#!/usr/bin/env python3
"""Derive keep_cjk.txt and need_glyphs.txt from the patched sources.

Only text inside string literals is counted. Scanning whole files pulled in
characters that appear only in comments (the vendor's traditional forms show
up in the doc comments), and those glyphs cost ~60 bytes each of a region B
that has almost nothing free.

    python derive_sets.py STOCK_CJK_SET_FILE PATCHED_SRC...

writes keep_cjk.txt (characters the vendor font already has) and
need_glyphs.txt (characters that must be drawn, in first-appearance order).
"""

import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
stock_path = sys.argv[1]
srcs = sys.argv[2:]

stock = set(io.open(stock_path, encoding="utf-8").read().strip())

# Drop // comments (the sources have no "//" inside a literal that matters),
# then take what sits between double quotes.
NO_COMMENT = re.compile(r"//[^\n]*")
LITERAL = re.compile(r'"([^"\n]*)"')


def wanted(ch):
    """Characters the font must carry: hanzi, plus the CJK punctuation the
    translations use (：，？！（）…、).

    The ranges `\\u3000-\\u303f` / `\\uff00-\\uffef` were left out at first and
    it went unnoticed: a glyph that is not in the font still *advances* the
    pen (one blank cell), so "边沿：" simply lost its colon instead of
    breaking the layout, and the confirm dialogs' 否 / 是 were blank.
    """
    o = ord(ch)
    return 0x4E00 <= o <= 0x9FFF or 0x3000 <= o <= 0x303F or 0xFF00 <= o <= 0xFFEF or o == 0x2026

seen = []
for p in srcs:
    text = io.open(p, encoding="utf-8").read()
    for m in LITERAL.finditer(NO_COMMENT.sub("", text)):
        for ch in m.group(1):
            if wanted(ch) and ch not in seen:
                seen.append(ch)

keep = [c for c in seen if c in stock]
draw = [c for c in seen if c not in stock]

io.open(os.path.join(HERE, "keep_cjk.txt"), "w", encoding="utf-8", newline="\n").write("".join(keep))
io.open(os.path.join(HERE, "need_glyphs.txt"), "w", encoding="utf-8", newline="\n").write("".join(draw))

sys.stderr.write("sources: %d\n" % len(srcs))
sys.stderr.write("CJK in literals: %d (%d from the vendor font, %d to draw)\n"
                 % (len(seen), len(keep), len(draw)))
sys.stderr.write("keep: %s\n" % "".join(keep))
sys.stderr.write("draw: %s\n" % "".join(draw))
