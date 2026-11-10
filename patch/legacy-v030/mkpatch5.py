#!/usr/bin/env python3
"""The last two settings values that can be Chinese without new glyphs.

Region B is at its floor: 8,452 bytes free, and the link fails below 8,192.
So these two are chosen to reuse characters the font already carries.

  danger::NAMES  Loud / Volume / Off -> 高 / 音量 / 关     (0 new glyphs:
                 高, 音, 量 and 关 are all already in the font)
  the DMM rate value in the settings page -> 慢 / 中 / 快   (2 new: 慢, 快)

`dmm::RATE_NAMES` itself must stay ASCII: app.rs also writes it into the SCPI
reply (`*IDN?`-style text over USBTMC/Bluetooth), where UTF-8 would corrupt
the protocol. Only the settings page's display picks the Chinese table.

    python mkpatch5.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "danger.rs": [
        ('pub const NAMES: [&str; 3] = ["Loud", "Volume", "Off"];',
         'pub const NAMES: [&str; 3] = ["\u9ad8", "\u97f3\u91cf", "\u5173"];'),
    ],
    "app.rs": [
        ('for part in [dmm::RATE_NAMES[self.dmm.rate() as usize], if applies { "  " } else { " (n/a here)" }, if applies { rps } else { "" }] {',
         'for part in [["\u6162", "\u4e2d", "\u5feb"][self.dmm.rate() as usize], if applies { "  " } else { " (n/a here)" }, if applies { rps } else { "" }] {'),
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
                sys.exit("%s: %d occurrences of %r" % (name, n, old[:70]))
            text = text.replace(old, new)
            total += 1
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-12s %d replacement(s)\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
