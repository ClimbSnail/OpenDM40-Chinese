#!/usr/bin/env python3
"""Move every ASCII26 user to TEXT22, so ASCII26 can be dropped entirely.

ASCII26 is a 26 px 4bpp RLE font: 6,279 bytes of bitmap plus 960 bytes of
entries, and it lives in region A2. It is the font behind every toast, every
dialog title and button, the gallery's labels and the boot splash.

TEXT22 is 22 px 1bpp. Switching costs a slightly smaller dialog font but buys:

  * A2: 6,279 B freed -- A2 had only 306 B left, so this is the only
        zero-wait space left in the whole image;
  * B : 960 B of entries freed;
  * and 64 B per hanzi (TEXT22) instead of ~150 B (4bpp) for the turns that
        follow.

Sites (found by grepping `ASCII26`):
  dialog.rs  centred_sp -- toasts, dialog text and buttons
  gallery.rs two labels
  splash.rs  "opendm40", the version, "Loading..."

    python mkpatch17.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "dialog.rs": [
        ('        sf::label(sf::ASCII26, rect(r.0 as i16, r.1 as i16, r.2 as i16, r.3 as i16), s, fg, bg, 8, spacing);',
         '        sf::label(sf::TEXT22, rect(r.0 as i16, r.1 as i16, r.2 as i16, r.3 as i16), s, fg, bg, 8, spacing);'),
    ],
    "gallery.rs": [
        ('sf::label(sf::ASCII26, r4(r), s, D_FG, bg, 8', 'sf::label(sf::TEXT22, r4(r), s, D_FG, bg, 8'),
        ('let mut font = sf::ASCII26;', 'let mut font = sf::TEXT22;'),
    ],
    "splash.rs": [
        ('sf::label(sf::ASCII26, rect(0, TOP, lcd::W as i16, 30), "opendm40", FG, BG, 8, 1);',
         'sf::label(sf::TEXT22, rect(0, TOP, lcd::W as i16, 30), "opendm40", FG, BG, 8, 1);'),
        ('sf::label(sf::ASCII26, rect(0, TOP + 32, lcd::W as i16, 30), ver, DIM, BG, 8, 1);',
         'sf::label(sf::TEXT22, rect(0, TOP + 32, lcd::W as i16, 30), ver, DIM, BG, 8, 1);'),
        ('sf::label(sf::ASCII26, rect(0, TOP + 74, lcd::W as i16, 30), "Loading...", DIM, BG, 8, 1);',
         'sf::label(sf::TEXT22, rect(0, TOP + 74, lcd::W as i16, 30), "Loading...", DIM, BG, 8, 1);'),
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
        sys.stderr.write("%-12s %d\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
