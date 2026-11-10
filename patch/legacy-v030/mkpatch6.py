#!/usr/bin/env python3
"""The range page's title and its Hold/Limits button, in Chinese.

Both use only characters the font already carries, so they cost no glyph:
电 压 设 置 流 阻 保 持 限 值.

Left English on purpose (each needs a new glyph, and region B is at its floor
of 8 KiB with 28 bytes to spare):
  "Wave"  -> 波形  would need 形
  "OK"    -> 确定  would need 定
  the "AUTO+ recommended: never steps to mV" note would need 降 / 安 / 全

    python mkpatch6.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

REPS = [
    ('Button::Volt => "Voltage Settings",', 'Button::Volt => "\u7535\u538b\u8bbe\u7f6e",'),
    ('Button::Amp => "Current Settings",', 'Button::Amp => "\u7535\u6d41\u8bbe\u7f6e",'),
    ('Button::Ohm => "Resistor Settings",', 'Button::Ohm => "\u7535\u963b\u8bbe\u7f6e",'),
    ('for (x, t) in [(8i16, "Hold/Limits"), (319, "OK")] {',
     'for (x, t) in [(8i16, "\u4fdd\u6301\u9650\u503c"), (319, "OK")] {'),
]


def main():
    path = os.path.join(SRC, "ui.rs")
    text = io.open(path, encoding="utf-8").read()
    for old, new in REPS:
        n = text.count(old)
        if n != 1:
            sys.exit("%d occurrences of %r" % (n, old[:60]))
        text = text.replace(old, new)
    io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("ui.rs: %d replacements (no new glyphs)\n" % len(REPS))


main()
