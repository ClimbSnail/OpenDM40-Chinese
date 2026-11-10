#!/usr/bin/env python3
"""The power meter: status texts and the button labels that cost nothing.

Region B has 76 bytes free, so this round is limited to strings whose
characters the font already carries -- plus one new glyph (零) if it still
fits.

Drawn with TEXT22, so all of these can be Chinese:

    pw_partial  "I ranging..."      -> 电流量程...     (0 new glyphs)
                "V calibration..."  -> 电压校准...     (0)
                "Zeroing: leads open" -> 清零中          (1: 零)
    settings_page / settings_press
                "V cal"   -> 电压校准   (0)
                "Reset Wh"-> 复位       (0)
                "Limits"  -> 限值       (0)
                "OK"      -> 确定       (0)

"At load" and "Wiring" stay English: 带载 / 接线 would need four more glyphs
(256 B) and there is no room.

Replaces every occurrence (the pressed-feedback path repeats the labels).

    python mkpatch16.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "powermeter.rs": [
        ('JOB_ZERO => "Zeroing: leads open",', 'JOB_ZERO => "\u6e05\u96f6\u4e2d",'),
        ('JOB_VCAL => "V calibration...",', 'JOB_VCAL => "\u7535\u538b\u6821\u51c6...",'),
        ('_ => "I ranging...",', '_ => "\u7535\u6d41\u91cf\u7a0b...",'),
    ],
    "ui_power.rs": [
        ('ps_button(ps_cell(2, 4), "V cal", false);',
         'ps_button(ps_cell(2, 4), "\u7535\u538b\u6821\u51c6", false);'),
        ('(PS_RESET, "Reset Wh")', '(PS_RESET, "\u590d\u4f4d")'),
        ('(PS_LIMITS, "Limits")', '(PS_LIMITS, "\u9650\u503c")'),
        ('(PS_OK, "OK")', '(PS_OK, "\u786e\u5b9a")'),
    ],
}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            n = text.count(old)
            if n == 0:
                sys.exit("%s: not found: %r" % (name, old[:60]))
            text = text.replace(old, new)
            total += n
            sys.stderr.write("%-14s %-40r x%d\n" % (name, old[:38], n))
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("total %d replacements\n" % total)


main()
