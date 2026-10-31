#!/usr/bin/env python3
"""Fix the recording toast: LOG000.DLG is 10 bytes, not 11.

The previous patch allocated `t[7..18]` (11 bytes) for an 8-byte name plus
digits and copied a 10-byte literal into it. `copy_from_slice` panics when the
lengths differ, so every stop of a CSV recording hit

    panicked at 'source slice length (10) does not match destination slice
    length (11)'

which draws the magenta panic bar, leaves the buzzer on and lets the watchdog
reset the meter -- exactly the "purple bar at the bottom, buzzer keeps sounding,
then it reboots" report. The screenshot toast used 8 for "S000.BMP" and was
right.

    python mkpatch28.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
APP = os.path.join(SRC, "app.rs")

app = io.open(APP, encoding="utf-8").read()


def sub(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    return text.replace(old, new)


app = sub(app,
          't[pre.len()..pre.len() + 11].copy_from_slice(b"LOG000.DLG");',
          't[pre.len()..pre.len() + 10].copy_from_slice(b"LOG000.DLG");',
          "log name copy")

app = sub(app,
          '(core::str::from_utf8(&t[..k + 11]).unwrap_or("已存"), true)',
          '(core::str::from_utf8(&t[..k + 10]).unwrap_or("已存"), true)',
          "log name slice")

io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("done: log name length fixed and named once\n")
