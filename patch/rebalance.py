#!/usr/bin/env python3
"""Move a few modules from region B into .cold, and set sane floors."""

import io
import sys

LINK = sys.argv[1]
lines = io.open(LINK, encoding="utf-8").read().split("\n")

WANT = [
    "*(.text.*8opendm404clock*);",
    "*(.text.*8opendm406hy3131*);",
    "*(.text.*8opendm406ad2pll*);",
]

present = []
for w in WANT:
    if any(w in line for line in lines):
        present.append(w)
missing = []
for w in WANT:
    if w not in present:
        missing.append(w)

out = []
for line in lines:
    if any(w in line for w in present):
        continue
    if "ASSERT" in line and "__b_end >=" in line:
        out.append('        ASSERT(0x08080000 - __b_end >= 8192, "region B free");')
        continue
    if "ASSERT" in line and "__image_end >=" in line:
        out.append('        ASSERT(0x080A0000 - __image_end >= 4096, "region C free");')
        continue
    out.append(line)
    if line.strip() == "*(.text.*8opendm406upload*);":
        for w in present:
            out.append("        " + w)

io.open(LINK, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("moved to .cold:", present)
print("not found:", missing)
