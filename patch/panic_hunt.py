#!/usr/bin/env python3
"""Hammer gestures and watch for the panic marker, with reconnect per step.

A panic fills the bottom 24 rows with MAGENTA (0xF81F) and stops feeding the
watchdog, so the marker is visible in a frame read within ~2 s. A gesture that
starts disk I/O (swipe-down on the DMM page toggles recording) legitimately
blocks DBG:LCD?, so those are skipped here.

Each step opens its own session: a crash drops the USB link, and the next step
reconnecting is itself the signal that the previous one died.

    python panic_hunt.py [rounds]
"""

import struct
import sys
import time

import pyvisa

W, H = 480, 320
ROUNDS = int(sys.argv[1]) if len(sys.argv) > 1 else 2


def parse_block(raw):
    if not raw.startswith(b"#"):
        return raw
    nd = int(raw[1:2])
    n = int(raw[2:2 + nd])
    return raw[2 + nd:2 + nd + n]


def open_meter():
    rm = pyvisa.ResourceManager("@py")
    names = [r for r in rm.list_resources() if "::4617::53312::" in r]
    if not names:
        return None
    return rm.open_resource(names[0], read_termination="\n", write_termination="\n", timeout=8000)


def magenta_fraction(d):
    n = int(W * 24 * 1.5 + 0.5)
    d.write("DBG:LCD? 0,%d,%d,%d,%d" % (H - 24, W, 24, 1 + n))
    raw = parse_block(d.read_raw())
    words = struct.unpack("<%dH" % (len(raw) // 2), raw)[1:]
    b = b"".join(struct.pack(">H", v) for v in words)
    hit = 0
    total = min(len(b) // 3, W * 24)
    for i in range(total):
        r, g, bl = b[3 * i], b[3 * i + 1], b[3 * i + 2]
        if r >= 0xF0 and g <= 0x30 and bl >= 0xF0:
            hit += 1
    return hit / max(total, 1)


GESTURES = [
    ("up on DMM",       "DBG:DRAG 240,250,240,90,300"),
    ("left on chart",   "DBG:DRAG 300,200,120,200,300"),
    ("right on chart",  "DBG:DRAG 120,200,300,200,300"),
    ("left top",        "DBG:DRAG 300,50,100,50,250"),
    ("right top",       "DBG:DRAG 100,50,300,50,250"),
    ("down fast",       "DBG:DRAG 240,60,240,280,80"),
    ("down slow",       "DBG:DRAG 240,60,240,280,900"),
    ("down hold",       "DBG:DRAG 240,60,240,280,300,600"),
    ("diag",            "DBG:DRAG 100,80,380,260,400"),
    ("diag rev",        "DBG:DRAG 380,80,100,260,400"),
    ("tap value",       "DBG:TAP 200,110"),
    ("tap chip",        "DBG:TAP 40,230"),
    ("tap key V",       "DBG:TAP 30,300"),
    ("tap key A",       "DBG:TAP 118,300"),
    ("tap key ohm",     "DBG:TAP 200,300"),
    ("tap key Hz",      "DBG:TAP 370,300"),
    ("tap key W",       "DBG:TAP 448,300"),
    ("menu",            "DBG:KEY 0,80"),
    ("run",             "DBG:KEY 1,80"),
    ("auto",            "DBG:KEY 2,80"),
    ("mf",              "DBG:KEY 3,80"),
    ("menu again",      "DBG:KEY 0,80"),
    ("menus 2",         "DBG:TAP 141,110"),
]

for r in range(ROUNDS):
    for name, cmd in GESTURES:
        d = open_meter()
        if d is None:
            print("!! meter disappeared before: %s  (crash?)" % name)
            sys.exit(2)
        try:
            d.write(cmd)
            time.sleep(0.30)
            frac = magenta_fraction(d)
        except Exception as e:
            print("!! %-16s link died: %s" % (name, e))
            print("   command: %s" % cmd)
            try:
                d.close()
            except Exception:
                pass
            time.sleep(2.5)
            d2 = open_meter()
            print("   reconnected: %s" % (d2 is not None))
            if d2 is not None:
                d2.close()
            sys.exit(2)
        try:
            d.close()
        except Exception:
            pass
        if frac > 0.25:
            print("!! PANIC MARKER after: %s  (magenta %.2f)" % (name, frac))
            print("   command: %s" % cmd)
            sys.exit(2)
    print("round %d clean (%d gestures)" % (r + 1, len(GESTURES)))

print("no panic marker")
