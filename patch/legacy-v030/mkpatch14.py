#!/usr/bin/env python3
"""The last English on the temperature screens.

The status line at the bottom of the temperature page is assembled from two
pieces, so both have to change:

    "Sensor current ~" ... " mA"   -> "传感器电流 ~" ...
    "Cold junction "   ... " C"    -> "冷端 " ...

The DMM page's sensor chip shows T_LABELS[sensor]; its first entry still read
"TC K" while the page button says K热电偶, so the chip follows.

Five new glyphs (传 感 器 冷 端) at about 64 B each; region B has 596 B.

    python mkpatch14.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "app.rs": [
        ('            put(b"Sensor current ~");', '            put("\u4f20\u611f\u5668\u7535\u6d41 ~".as_bytes());'),
        ('            put(b"Cold junction ");', '            put("\u51b7\u7aef ".as_bytes());'),
    ],
    "ui.rs": [
        ('pub const T_LABELS: [&str; 7] = ["TC K", "PT100", "PT1000", "NTC10k B3950", '
         '"NTC10k B3435", "NTC100k B3950", "NTC user"];',
         'pub const T_LABELS: [&str; 7] = ["K\u70ed\u7535\u5076", "PT100", "PT1000", "NTC10k B3950", '
         '"NTC10k B3435", "NTC100k B3950", "NTC\u81ea\u5b9a\u4e49"];'),
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
