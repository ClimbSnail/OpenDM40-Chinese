#!/usr/bin/env python3
"""Reproduce the record-toggle trouble, carefully.

Swipe-down on the DMM page starts/stops the CSV log. The earlier stress run lost
the link right there, so each step here:

  * starts a recording, waits, stops it, waits,
  * then asks DBG:PING? for liveness (a cheap command that does not touch the
    panel, unlike DBG:LCD?) and reads the bottom strip for the panic marker,
  * and only then reads the panel, after the disk has gone quiet.

Any step that throws is reported instead of aborting, so one hang still tells us
where it happened.

    python rec_hunt.py [rounds]
"""

import struct
import sys
import time

import pyvisa

W, H = 480, 320
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 5


def parse_block(raw):
    if not raw.startswith(b"#"):
        return raw
    nd = int(raw[1:2])
    n = int(raw[2:2 + nd])
    return raw[2 + nd:2 + nd + n]


rm = pyvisa.ResourceManager("@py")
names = [r for r in rm.list_resources() if "::4617::53312::" in r]
if not names:
    sys.exit("meter not found")
d = rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=12000)


def step(label, fn):
    try:
        return fn()
    except Exception as e:
        print("  %-18s FAIL: %s" % (label, type(e).__name__ + ": " + str(e)[:60]))
        return None


def alive():
    d.write("DBG:PING?")
    return d.read().strip()


def magenta():
    n = int(W * 24 * 1.5 + 0.5)
    d.write("DBG:LCD? 0,%d,%d,%d,%d" % (H - 24, W, 24, 1 + n))
    raw = parse_block(d.read_raw())
    words = struct.unpack("<%dH" % (len(raw) // 2), raw)[1:]
    b = b"".join(struct.pack(">H", v) for v in words)
    total = max(min(len(b) // 3, W * 24), 1)
    hit = sum(1 for i in range(total)
              if b[3 * i] >= 0xF0 and b[3 * i + 1] <= 0x30 and b[3 * i + 2] >= 0xF0)
    return hit / total


for r in range(ROUNDS):
    print("round %d" % (r + 1))
    step("start recording", lambda: d.write("DBG:DRAG 240,90,240,250,300"))
    time.sleep(2.5)
    print("   alive:", step("ping", alive))
    print("   magenta:", step("marker", magenta))

    step("stop recording", lambda: d.write("DBG:DRAG 240,90,240,250,300"))
    time.sleep(2.5)
    ping = step("ping", alive)
    print("   alive after stop:", ping)
    frac = step("marker", magenta)
    print("   magenta after stop:", frac)
    if frac is not None and frac > 0.25:
        print("!! PANIC on stop, round %d" % (r + 1))
        sys.exit(2)
    if ping is None:
        print("!! lost the link on stop, round %d" % (r + 1))
        sys.exit(3)
    time.sleep(0.5)

print("no panic, link held")
