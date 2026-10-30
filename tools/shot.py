#!/usr/bin/env python3
"""Grab the meter's screen over USBTMC (PyVISA), on Windows.

Upstream dm40dbg.py does this too but finds the meter through /sys/bus/usb,
so it is Linux only. Protocol (src/lcd.rs, tools/dm40dbg.py cmd_shot):

    DBG:LCD? x,y,w,h,nwords   ->  IEEE 488.2 definite block of 16-bit words
    the first word is a dummy;  rgb666 packs 3 bytes per pixel big-endian
    into the words, so 1.5 words per pixel.

    python shot.py out.png [--format rgb565|rgb666] [--rows 4]
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
    out = argv[0] if argv else "screen.png"
    fmt = argv[argv.index("--format") + 1] if "--format" in argv else "rgb666"
    rows = int(argv[argv.index("--rows") + 1]) if "--rows" in argv else 4
    per_px = 1.0 if fmt == "rgb565" else 1.5

    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r]
    if not names:
        sys.exit("meter not found over USBTMC")
    d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=15000)

    img = Image.new("RGB", (W, H))
    px = img.load()
    t0 = time.time()

    for y in range(0, H, rows):
        n = int(W * rows * per_px + 0.5)
        d.write("DBG:LCD? 0,%d,%d,%d,%d" % (y, W, rows, 1 + n))
        raw = parse_block(d.read_raw())
        words = list(struct.unpack("<%dH" % (len(raw) // 2), raw))[1:]

        if fmt == "rgb565":
            for i in range(min(len(words), W * rows)):
                v = words[i]
                px[i % W, y + i // W] = ((v >> 8) & 0xF8, (v >> 3) & 0xFC, (v << 3) & 0xF8)
        else:
            b = b"".join(struct.pack(">H", v) for v in words)
            for i in range(min(len(b) // 3, W * rows)):
                r, g, bl = b[3 * i:3 * i + 3]
                px[i % W, y + i // W] = (r & 0xFC, g & 0xFC, bl & 0xFC)
        sys.stderr.write("\r  row %d/%d" % (min(y + rows, H), H))
        sys.stderr.flush()

    sys.stderr.write("\n")
    img.save(out)
    print("saved %s in %.1f s" % (out, time.time() - t0))


main()
