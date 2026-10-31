#!/usr/bin/env python3
"""Tap, then read the panel immediately -- for toasts that live ~1-2 s.

Starting a fresh python + pyvisa per step costs about a second, which is most
of the toast's life. This opens one session, taps, then grabs the frame.
"""

import struct
import sys
import time

import pyvisa
from PIL import Image

W, H, ROWS = 480, 320, 4
X, Y = int(sys.argv[1]), int(sys.argv[2])
OUT = sys.argv[3]


def parse_block(raw):
    if not raw.startswith(b"#"):
        return raw
    nd = int(raw[1:2])
    n = int(raw[2:2 + nd])
    return raw[2 + nd:2 + nd + n]


rm = pyvisa.ResourceManager("@py")
names = [r for r in rm.list_resources() if "::4617::53312::" in r]
d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=15000)

d.write("DBG:TAP %d,%d" % (X, Y))
time.sleep(0.35)

img = Image.new("RGB", (W, H))
px = img.load()
for y in range(0, H, ROWS):
    n = int(W * ROWS * 1.5 + 0.5)
    d.write("DBG:LCD? 0,%d,%d,%d,%d" % (y, W, ROWS, 1 + n))
    raw = parse_block(d.read_raw())
    words = struct.unpack("<%dH" % (len(raw) // 2), raw)[1:]
    b = b"".join(struct.pack(">H", v) for v in words)
    for i in range(min(len(b) // 3, W * ROWS)):
        r, g, bl = b[3 * i:3 * i + 3]
        px[i % W, y + i // W] = (r & 0xFC, g & 0xFC, bl & 0xFC)
img.save(OUT)
print("saved", OUT)
