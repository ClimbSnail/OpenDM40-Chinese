#!/usr/bin/env python3
"""Set the region-B free floor to an explicit byte count."""

import io
import sys

LINK = sys.argv[1]
FLOOR = sys.argv[2]

lines = io.open(LINK, encoding="utf-8").read().split("\n")
fixed = []
for line in lines:
    if "ASSERT" in line and "__b_end >=" in line:
        fixed.append(
            '        ASSERT(0x08080000 - __b_end >= %s, "region B free");' % FLOOR
        )
    else:
        fixed.append(line)

io.open(LINK, "w", encoding="utf-8", newline="\n").write("\n".join(fixed))
print("B floor", FLOOR)
