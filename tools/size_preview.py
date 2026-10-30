#!/usr/bin/env python3
"""Render candidate Chinese labels at the two sizes the UI uses, so the
legibility question is answered by pixels instead of opinion.

F14  : 14 px, 1 bpp  -- the DMM page's small labels (MAX / AVG / MIN / REL,
                       the rate chip, "ms/div", the axis numbers)
TEXT22: 22 px, 1 bpp -- settings labels, page titles, the main menu

Output: one PNG, each sample drawn at 1x and at 4x nearest-neighbour so the
dots are visible.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

FONT = "C:\\Windows\\Fonts\\simsun.ttc"
OUT = "F:\\desk\\study\\dm40\\shots\\glyph-size-comparison.png"

SIZES = [(14, "F14  14px (DMM small labels)"), (22, "TEXT22 22px (menus, settings)")]
SAMPLES = ["最大", "平均", "最小", "相对", "记录", "保持", "量程", "蜂鸣音量"]

SCALE = 4
PAD = 6
LABEL_H = 16

rows = []
for size, title in SIZES:
    font = ImageFont.truetype(FONT, size)
    cells = []
    for s in SAMPLES:
        img = Image.new("L", (size * len(s), size), 0)
        ImageDraw.Draw(img).text((0, size), s, font=font, fill=255, anchor="ls")
        # binarise exactly like the glyph pipeline does
        px = img.load()
        for y in range(size):
            for x in range(size * len(s)):
                px[x, y] = 255 if px[x, y] >= 110 else 0
        cells.append(img)
    w = sum(c.width for c in cells) + PAD * (len(cells) + 1)
    rows.append((title, cells, w, size))

W = max(r[2] for r in rows)
H = sum(LABEL_H + r[3] * SCALE + PAD for r in rows) + PAD

out = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(out)
small = ImageFont.truetype(FONT, 13)
y = PAD
for title, cells, w, size in rows:
    d.text((PAD, y), title, font=small, fill=170)
    y += LABEL_H
    x = PAD
    for c in cells:
        big = c.resize((c.width * SCALE, size * SCALE), Image.NEAREST)
        out.paste(big, (x, y))
        x += c.width * SCALE + PAD * SCALE
    y += size * SCALE + PAD

out.save(OUT)
print("saved %s (%dx%d)" % (OUT, out.width, out.height))
