#!/usr/bin/env python3
"""Dialog buttons in Chinese.

After mkpatch17 every dialog and toast is drawn with TEXT22, so a hanzi costs
64 B instead of the ~150 B it would have cost in the 4bpp ASCII26. Dropping
ASCII26 also freed its 960 B entry table from region B, which is what paid for
this.

Buttons (drawn by `button()` -> `centred()` -> `centred_sp`):
    Yes -> 是     No -> 否
    Cancel -> 取消   Start -> 开始   Again -> 再次

    python mkpatch18.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "dialog.rs": [
        ('button(NO, "No", BTN);', 'button(NO, "\u5426", BTN);'),
        ('button(YES, "Yes", BTN_RED);', 'button(YES, "\u662f", BTN_RED);'),
    ],
    "app.rs": [
        ('Some("Cancel")', 'Some("\u53d6\u6d88")'),
        ('Some("Start")', 'Some("\u5f00\u59cb")'),
        ('Some("Again")', 'Some("\u518d\u6b21")'),
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
                sys.exit("%s: not found: %r" % (name, old[:50]))
            text = text.replace(old, new)
            total += n
            sys.stderr.write("%-10s %-22r x%d\n" % (name, old[:20], n))
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("total %d\n" % total)


main()
