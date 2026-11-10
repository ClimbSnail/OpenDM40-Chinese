#!/usr/bin/env python3
"""The generator's waveform names, paid for by trimming the help page.

`gen_wave_box` draws the name with TEXT22, so 正弦 / 方波 / 三角 / 上升 are
possible. 上升 is chosen over 斜坡 so only one new glyph is needed (上 is
already in the font for 上限).

`logic level` next to Vpp stays English on purpose: `gen_box_note` draws it
with F14 (14 px, 12 px row pitch), the same font that forced MAX/AVG/MIN to
stay English.

Money: five new glyphs cost about 320 B and region B had 164 B, so the help
page keeps its title and first four rows and gives up the rest -- roughly
175 B of English prose that the manual already covers.

    python mkwave.py FIRMWARE_SRC_DIR
"""

import io
import os
import re
import sys

SRC = sys.argv[1]

# ---- 1. waveform names ------------------------------------------------
GEN = os.path.join(SRC, "genplan.rs")
t = io.open(GEN, encoding="utf-8").read()

REPS = [
    ('            Wave::Sine => "Sine",', '            Wave::Sine => "\u6b63\u5f26",'),
    ('            Wave::Square => "Square",', '            Wave::Square => "\u65b9\u6ce2",'),
    ('            Wave::Triangle => "Triangle",', '            Wave::Triangle => "\u4e09\u89d2",'),
    ('            Wave::Ramp => "Ramp",', '            Wave::Ramp => "\u4e0a\u5347",'),
]
for old, new in REPS:
    if t.count(old) != 1:
        sys.exit("genplan.rs: %d occurrences of %r" % (t.count(old), old.strip()))
    t = t.replace(old, new)
io.open(GEN, "w", encoding="utf-8", newline="\n").write(t)
sys.stderr.write("genplan.rs: 4 wave names\n")

# ---- 2. help page: keep four rows -------------------------------------
UI = os.path.join(SRC, "ui.rs")
u = io.open(UI, encoding="utf-8").read()

m = re.search(r'\n    \(\n        "Gestures",\n        \[\n(.*?)\n        \],\n    \),', u, re.S)
if not m:
    sys.exit("Gestures block not found")

rows = re.findall(r'            \("[^"]*", "[^"]*"\),', m.group(1))
if len(rows) != 8:
    sys.exit("Gestures has %d rows, expected 8" % len(rows))

kept = rows[:4]
blank = ['            ("", ""),'] * 4
new_block = "\n".join(kept + blank)
u = u[:m.start(1)] + "\n" + new_block + u[m.end(1):]
io.open(UI, "w", encoding="utf-8", newline="\n").write(u)
sys.stderr.write("ui.rs: help page 8 -> 4 rows\n")
