#!/usr/bin/env python3
"""Reverted: the DMM page's 14 px labels stay English.

Attempted and measured on the meter; both variants looked bad, so this file is
deliberately a no-op that records why.

The labels live in `F14`: 14 px tall, 1 bpp, line_h 14 / descent 3, and the
rows they sit on are 12 px apart (SIDE_Y 176, 188, 245, 259) while
`stockfont::label` clips to its rect.

  * 14 px hanzi: ink is 14 rows, the row pitch is 12 and the label rect is 14
    -- no margin anywhere, and the renderer's baseline puts the bottom row
    outside the clip window.
  * 11 px hanzi: fits geometrically (ink 9-10 rows, ink rows 1..10), and the
    encoding was fixed to the vendor convention (h = ink height, t = 0,
    yoff places it). On the meter "相对" came out as thin scattered pixels and
    "格" in "320ms/格" lost most of its strokes: 11 px of 1 bpp is simply not
    enough for 木 + 各 or 相 + 对.

So F14 is left alone. The Chinese that ships is all in `TEXT22` (22 px, 1 bpp,
the vendor's own hanzi plus 34 drawn), which the screenshots show to be
consistent with the vendor glyphs and free of clipping.

Usage (still supported so the pipeline stays one command):
    python mkpatch3.py IN_UI_RS OUT_UI_RS
"""

import io
import shutil
import sys

SRC, DST = sys.argv[1], sys.argv[2]
shutil.copyfile(SRC, DST)
sys.stderr.write("mkpatch3: no-op (F14 labels stay English; see the docstring)\n")
