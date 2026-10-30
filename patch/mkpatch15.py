#!/usr/bin/env python3
"""Range-page titles for the four functions that fell through to the default.

`range_title` only named Volt / Amp / Ohm; every other function matched `_` and
therefore showed "Capacitance Settings" -- so the capacitance, diode/continuity
and Hz/temperature pages all carried the wrong header, in English.

Now:
    Cap        -> 电容设置      (new glyph: 容)
    ContDiode  -> 二极管        (new glyphs: 二 极 管)
    HzTemp     -> 频率/温度     (no new glyphs)
    _          -> 功率设置       (no new glyphs)

Also the ohm variant button's stock tag:

    "0.28 mA ON" -> "0.28 mA 开"   (no new glyphs)

Four new glyphs, about 256 B; region B has 356 B.

    python mkpatch15.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui.rs": [
        ('        Button::Ohm => "\u7535\u963b\u8bbe\u7f6e",\n        _ => "Capacitance Settings",\n    };',
         '        Button::Ohm => "\u7535\u963b\u8bbe\u7f6e",\n'
         '        Button::Cap => "\u7535\u5bb9\u8bbe\u7f6e",\n'
         '        Button::ContDiode => "\u4e8c\u6781\u7ba1",\n'
         '        Button::HzTemp => "\u9891\u7387/\u6e29\u5ea6",\n'
         '        _ => "\u529f\u7387\u8bbe\u7f6e",\n    };'),
        ('pub const OHM_VARS: [&str; 2] = ["0.90 mA", "0.28 mA ON"];',
         'pub const OHM_VARS: [&str; 2] = ["0.90 mA", "0.28 mA \u5f00"];'),
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
    sys.stderr.write("total %d\n" % total)


main()
