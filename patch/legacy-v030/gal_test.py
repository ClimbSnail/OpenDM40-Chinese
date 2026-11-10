#!/usr/bin/env python3
"""Gallery batch delete test."""

import struct
import sys
import time

import pyvisa
from PIL import Image

W, H = 480, 320
ROWS = 4


def open_meter():
    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r]
    if not names:
        return None
    return rm.open_resource(names[0], read_termination="\n",
                            write_termination="\n", timeout=12000)


def parse_block(raw):
    if not raw.startswith(b"#"):
        return raw
    nd = int(raw[1:2])
    n = int(raw[2:2 + nd])
    return raw[2 + nd:2 + nd + n]


def shot(d, path):
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
    img.save(path)


def boot_reason(d):
    d.write("DBG:BOOT?")
    return d.read().split(",")[3]


rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
d = open_meter()
if d is None:
    sys.exit("meter not found")

print("start:", boot_reason(d))
for r in range(rounds):
    print("--- round", r + 1, "---")
    d.write("DBG:KEY 0,60")
    time.sleep(1.0)
    d.write("DBG:TAP 250,30")
    time.sleep(2.0)
    d.write("DBG:TAP 240,300")
    time.sleep(0.8)
    d.write("DBG:TAP 80,110")
    time.sleep(0.6)
    d.write("DBG:TAP 240,110")
    time.sleep(0.8)
    shot(d, r"F:\desk\study\build\gt%d-before.png" % (r + 1))
    d.write("DBG:TAP 415,300")
    time.sleep(5.0)
    shot(d, r"F:\desk\study\build\gt%d-after.png" % (r + 1))
    print("after delete:", boot_reason(d))
print("done")
