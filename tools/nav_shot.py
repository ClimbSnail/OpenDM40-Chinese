#!/usr/bin/env python3
"""Navigate the meter and capture the screen in one USBTMC session.

    python nav_shot.py --menus 3 --tap 141,110 --out shot.png
    python nav_shot.py --out shot.png

Each MENU press is a separate USBTMC message with a delay, because the meter
debounces the side keys; a tap lands after the last MENU.
"""

import struct
import sys
import time

import pyvisa
from PIL import Image

W, H = 480, 320


def parse_block(raw):
    if not raw.startswith(b"#"):
        return raw
    nd = int(raw[1:2])
    n = int(raw[2:2 + nd])
    return raw[2 + nd:2 + nd + n]


def main():
    argv = sys.argv[1:]

    def opt(n, d=None):
        return argv[argv.index(n) + 1] if n in argv else d

    menus = int(opt("--menus", "0"))
    tap = opt("--tap")
    out = opt("--out", "shot.png")
    rows = 4

    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r]
    if not names:
        sys.exit("meter not found")
    d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=15000)

    for _ in range(menus):
        d.write("DBG:KEY 0,120")
        time.sleep(0.9)
    if tap:
        d.write("DBG:TAP %s" % tap)
        time.sleep(1.2)

    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(0, H, rows):
        n = int(W * rows * 1.5 + 0.5)
        d.write("DBG:LCD? 0,%d,%d,%d,%d" % (y, W, rows, 1 + n))
        raw = parse_block(d.read_raw())
        words = list(struct.unpack("<%dH" % (len(raw) // 2), raw))[1:]
        b = b"".join(struct.pack(">H", v) for v in words)
        for i in range(min(len(b) // 3, W * rows)):
            r, g, bl = b[3 * i:3 * i + 3]
            px[i % W, y + i // W] = (r & 0xFC, g & 0xFC, bl & 0xFC)
    img.save(out)
    print("saved %s" % out)


main()
