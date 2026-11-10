#!/usr/bin/env python3
"""The rest of the toasts, the firmware dialog and the wiring dialog title.

All of these are TEXT22 now, 64 B per hanzi, and region B has 3,892 B usable.

    python mkpatch21.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui_power.rs": [
        ('"Power meter: wiring"', '"\u529f\u7387\u8ba1\u63a5\u7ebf"'),
    ],
    "dialog.rs": [
        ('pub const FW_TITLE: &str = "Firmware received";',
         'pub const FW_TITLE: &str = "\u56fa\u4ef6\u5df2\u63a5\u6536";'),
        ('pub const FW_BODY: &str = "Install it now?";',
         'pub const FW_BODY: &str = "\u73b0\u5728\u5b89\u88c5\uff1f";'),
        ('pub const FW_BAD: &str = "Not a DM40 update file";',
         'pub const FW_BAD: &str = "\u4e0d\u662f DM40 \u5347\u7ea7\u6587\u4ef6";'),
        ('pub const AUTO_DC: &str = "AUTO: DC (no AC signal)";',
         'pub const AUTO_DC: &str = "\u81ea\u52a8: \u76f4\u6d41 (\u65e0\u4ea4\u6d41\u4fe1\u53f7)";'),
    ],
    "app.rs": [
        ('"Fixed rate in this function"', '"\u6b64\u529f\u80fd\u56fa\u5b9a\u901f\u7387"'),
        ('"Fast: DC/AC V or A only"', '"\u5feb\u901f\u4ec5\u9650 V/A"'),
        ('"Installing firmware..."', '"\u6b63\u5728\u5b89\u88c5\u56fa\u4ef6..."'),
        ('"Re-plug USB to apply"', '"\u8bf7\u91cd\u63d2 USB \u751f\u6548"'),
    ],
    "app_power.rs": [
        ('"Current too high: reduce it"', '"\u7535\u6d41\u8fc7\u5927, \u8bf7\u964d\u4f4e"'),
    ],
    "app_wave.rs": [
        ('"Wave: no AD2 row here"', '"\u6ce2\u5f62: \u6b64\u5904\u65e0 AD2"'),
        ('"DC-coupled AC row"', '"\u4ea4\u6d41\u6863\u4e3a\u76f4\u6d41\u8026\u5408"'),
    ],
    "scope_page.rs": [
        ('"Disk busy, try again"', '"\u78c1\u76d8\u5fd9, \u8bf7\u91cd\u8bd5"'),
        ('"Save CSV Error"', '"\u4fdd\u5b58\u51fa\u9519"'),
        ('"Saving CSV..."', '"\u6b63\u5728\u4fdd\u5b58..."'),
        ('"Saving CSV, wait"', '"\u6b63\u5728\u4fdd\u5b58, \u8bf7\u7a0d\u5019"'),
        ('"Wave: data logger running"', '"\u6ce2\u5f62: \u8bb0\u5f55\u8fd0\u884c\u4e2d"'),
        ('"AUTO: no signal found"', '"\u81ea\u52a8: \u672a\u627e\u5230\u4fe1\u53f7"'),
    ],
    "app_touchtest.rs": [
        ('"Touch calibration saved"', '"\u89e6\u6478\u6821\u51c6\u5df2\u4fdd\u5b58"'),
        ('"Touch calibration reset"', '"\u89e6\u6478\u6821\u51c6\u5df2\u590d\u4f4d"'),
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
                sys.stderr.write("%-16s MISS %r\n" % (name, old[:46]))
                continue
            text = text.replace(old, new)
            total += n
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-16s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
