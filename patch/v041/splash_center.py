#!/usr/bin/env python3
"""Centre the boot splash's block on the panel.

The splash draws four things at fixed offsets from `TOP` in `splash.rs` --
"opendm40" (TOP), the version (TOP + 32), "载入中..." (TOP + 74) and the
progress bar (TOP + 114) -- with the wordmark picture (`splash_img.rs`, 47 px
tall) 19 px above the text: its bottom sits at TOP - 19. On the 320 px panel
that block ran y 18..206, i.e. 94 px of empty panel above it and 114 below, so
everything read as "too high" (owner 2026-08.. 2026-11-10: "开机动画的文字有点
偏高，相对居中").

A block that is centred has equal margins: the block is 188 px tall
(picture 47 + 19 + 122), so its top goes at (320 - 188) / 2 = 66 and the first
text line 66 + 65 + 1 = 132. The wordmark is placed by the generator
(`gen_splash_img2.py`: Y = TEXT_TOP - H - 19); this script only moves `TOP`
and the note stays the fixed distance below the bar (it is drawn on a slow
first start only).

    splash_center.py --src firmware/src

Idempotent: a tree that already has the centred offsets is left alone.
"""

import argparse
import io
import os
import sys

OLD = """/// Top of "opendm40"; the version, "载入中...", the bar and the note
/// below it at fixed offsets: the block without the note sits a little
/// above the 320-px screen's centre, with the note a little below.
const TOP: i16 = 84;
"""

NEW = """/// Top of "opendm40"; the version, "载入中...", the bar and the note
/// below it at fixed offsets. Together with the wordmark above it (its
/// bottom sits 19 px over TOP) the always-drawn block runs TOP - 66 ..
/// TOP + 122: with TOP = 132 that is the 320-px panel's centre (66 px of
/// margin above and below). The note, drawn only on a slow first start,
/// goes below the bar, where it still fits (its last row ends at 317).
const TOP: i16 = 132;
"""


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    a = p.parse_args()

    path = os.path.join(a.src, "splash.rs")
    text = io.open(path, encoding="utf-8").read()

    if "const TOP: i16 = 132;" in text:
        print("splash.rs: already centred (TOP = 132)")
        return

    n = text.count(OLD)
    if n != 1:
        sys.exit("splash.rs: expected 1 hit, found %d -- upstream changed, fix the anchor" % n)

    io.open(path, "w", encoding="utf-8", newline="\n").write(text.replace(OLD, NEW))
    print("splash.rs: TOP 84 -> 132 (block centred: 66 px above and below)")


if __name__ == "__main__":
    main()
