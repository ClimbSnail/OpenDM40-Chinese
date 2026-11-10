#!/usr/bin/env python3
"""The limits page's title bar and its ON/OFF values.

Found by looking at the meter after mkpatch9: the rows were Chinese but the
title still read "Hold & Limits: DC V" and the values were still ON / OFF.

Both reuse characters the font already has (保 持 限 值 开 关), so this costs
no new glyphs -- which matters, because region B is at 8,348 B free against a
8,192 B floor.

`onoff` is a closure local to limits_page (app.rs:1202), not a shared helper,
so changing it cannot leak into SCPI replies.

    python mkpatch12.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "app.rs": [
        # the title prefix; the coupling name after it stays ASCII ("DC V")
        ('        let pre = b"Hold & Limits: ";\n        t[..pre.len()].copy_from_slice(pre);',
         '        let pre = "\u4fdd\u6301\u9650\u503c: ";\n        t[..pre.len()].copy_from_slice(pre.as_bytes());'),
        # row values: ON / OFF
        ('        let onoff = |b: bool| if b { "ON" } else { "OFF" };',
         '        let onoff = |b: bool| if b { "\u5f00" } else { "\u5173" };'),
    ],
}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            n = text.count(old)
            if n != 1:
                sys.exit("%s: %d occurrences of %r" % (name, n, old[:60]))
            text = text.replace(old, new)
            total += 1
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-10s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d (0 new glyphs)\n" % total)


main()
