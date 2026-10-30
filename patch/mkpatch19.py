#!/usr/bin/env python3
"""The toasts people actually see while using the meter.

Now that toasts are drawn with TEXT22 (mkpatch17), a hanzi costs 64 B and
region B has 620 B to spare. These are the frequent, self-explanatory ones;
the rarer per-page messages stay English for now.

    "Recording CSV"          -> 正在记录
    "No reading to log"      -> 无数值可记录
    "Stop the recording first" -> 请先停止记录
    "Saving CSV..."          -> 正在保存...
    "Saving CSV, wait"       -> 正在保存, 请稍候
    "Disk busy, try again"   -> 磁盘忙, 请重试
    "Fixed rate in this function" -> 此功能固定速率

    python mkpatch19.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

REPS = [
    ('self.toast(now, "Recording CSV", true);',
     'self.toast(now, "\u6b63\u5728\u8bb0\u5f55", true);'),
    ('self.toast(now, "No reading to log", false);',
     'self.toast(now, "\u65e0\u6570\u503c\u53ef\u8bb0\u5f55", false);'),
    ('self.toast(now, "Stop the recording first", false);',
     'self.toast(now, "\u8bf7\u5148\u505c\u6b62\u8bb0\u5f55", false);'),
]

JOBS = {"app.rs": REPS}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            n = text.count(old)
            if n == 0:
                sys.exit("%s: not found: %r" % (name, old[:55]))
            text = text.replace(old, new)
            total += n
            sys.stderr.write("%-10s %-40r x%d\n" % (name, old[:36], n))
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("total %d\n" % total)


main()
