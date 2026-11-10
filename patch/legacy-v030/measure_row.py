#!/usr/bin/env python3
"""Measure each character's ink rows in a screenshot row, to the pixel.

Eyeballing a 5x zoom is not proof. This walks the label columns (22 px advance)
of one list row and reports, per character, the first and last row that has
ink. Characters that share a baseline end on the same row.
"""

import sys

from PIL import Image

PATH = sys.argv[1]
Y0, Y1 = int(sys.argv[2]), int(sys.argv[3])
X0, ADV, N = int(sys.argv[4]), 22, int(sys.argv[5])
THR = 90

im = Image.open(PATH).convert("L")
px = im.load()

for k in range(N):
    x = X0 + k * ADV
    rows = []
    for y in range(Y0, Y1):
        if any(px[x + i, y] >= THR for i in range(ADV) if x + i < im.width):
            rows.append(y)
    if rows:
        print("  char %d: x=%3d  ink rows %d..%d  (top offset %d, height %d)"
              % (k, x, rows[0], rows[-1], rows[0] - Y0, rows[-1] - rows[0] + 1))
    else:
        print("  char %d: x=%3d  (blank)" % (k, x))
