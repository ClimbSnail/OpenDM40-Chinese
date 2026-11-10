#!/usr/bin/env python3
"""The temperature page, plus the pressed-feedback strings I had missed.

Region A2 turned out to have 1,128 bytes free (zero-wait, same speed as B), so
two icon fonts that are redrawn only when a badge changes move there. That
frees 822 B in region B, enough for the nine new glyphs this page needs.

Temperature page (all TEXT22):
    T_KEYS[0]  "TC K"      -> "K热电偶"
    T_KEYS[6]  "NTC user"  -> "NTC自定义"
    "Unit: C" / "Unit: F"  -> "单位: C" / "单位: F"
    hint line              -> "点数值可输入"
    PT100 / PT1000 / 10k 3950 / 10k 3435 / 100k 3950 stay: they are standard
    sensor designations, not English prose.

Free (0 new glyphs, they were simply duplicated in the pressed-feedback path):
    "Hold/Limits" -> 保持限值      "OK"     -> 确定
    "Fuse check"  -> 保险丝自检     "Inrush" -> 涌流
Those only show for the frame while a button is held down, which is why they
survived the earlier sweep.

    python mkpatch13.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui.rs": [
        # ---- temperature page: sensor keys ---------------------------
        ('const T_KEYS: [&str; 7] = ["TC K", "PT100", "PT1000", "10k 3950", "10k 3435", "100k 3950", "NTC user"];',
         'const T_KEYS: [&str; 7] = ["K\u70ed\u7535\u5076", "PT100", "PT1000", "10k 3950", "10k 3435", '
         '"100k 3950", "NTC\u81ea\u5b9a\u4e49"];'),
        ('TK_UNIT => if p.unit_f { "Unit: F" } else { "Unit: C" },',
         'TK_UNIT => if p.unit_f { "\u5355\u4f4d: F" } else { "\u5355\u4f4d: C" },'),
        # ---- temperature page: the hint line -------------------------
        ('let hint = if p.sensor == 0 { "Tap the value to type it (TC: on the CJ)" } '
         'else { "Tap the value to type it" };',
         'let hint = if p.sensor == 0 { "\u70b9\u6570\u503c\u53ef\u8f93\u5165" } '
         'else { "\u70b9\u6570\u503c\u53ef\u8f93\u5165" };'),
        # ---- pressed-feedback copies (0 new glyphs) ------------------
        ('TK_LIMITS => "Hold/Limits",', 'TK_LIMITS => "\u4fdd\u6301\u9650\u503c",'),
        ('        _ => "OK",\n    };', '        _ => "\u786e\u5b9a",\n    };'),
        ('(2, _) => (rect(319, 240, 150, 38), "OK", false),',
         '(2, _) => (rect(319, 240, 150, 38), "\u786e\u5b9a", false),'),
        ('(4, _) => (rect(8, 240, 150, 38), "Hold/Limits", false),',
         '(4, _) => (rect(8, 240, 150, 38), "\u4fdd\u6301\u9650\u503c", false),'),
        ('(5, Button::Amp) => (FUSE_BTN, "Fuse check", false),',
         '(5, Button::Amp) => (FUSE_BTN, "\u4fdd\u9669\u4e1d\u81ea\u68c0", false),'),
        ('RP_INRUSH => (INRUSH_BTN, "Inrush", false),',
         'RP_INRUSH => (INRUSH_BTN, "\u6d8c\u6d41", false),'),
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
                sys.exit("%s: %d occurrences of %r" % (name, n, old[:65]))
            text = text.replace(old, new)
            total += 1
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-10s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
