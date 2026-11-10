#!/usr/bin/env python3
"""Line-based fix for link-native.x: drop the SCPI rule, floor B at 6 KiB."""

import io
import sys

LINK = sys.argv[1]
lines = io.open(LINK, encoding="utf-8").read().split("\n")

out = []
dropped = 0
for l in lines:
    if "8opendm404scpi*" in l:
        dropped += 1
        continue
    if "__b_end >=" in l and "ASSERT" in l:
        l = ('ASSERT(0x08080000 - __b_end >= 6K, "less than 6 KiB of zero-wait flash '
             '(region B) free: the gallery batch delete took ~2.9 KB; move rarely run code to .cold");')
    out.append(l)

io.open(LINK, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("dropped %d scpi line(s), B floor 6 KiB" % dropped)
