#!/usr/bin/env python3
"""Trim the on-device help from 7 pages to 4, to free flash for glyphs.

Kept, because nothing else on the meter mentions them:
  0 Gestures          three-finger screenshot, two-finger power off, ...
  1 Side keys         RUN held = AutoHold, power key twice = touch lock, ...
  2 Multimeter        history store/clear, MIN/MAX session, REL, ...
  3 Limits            keeps the "Gen output: never apply voltage" warning,
                      the one safety line that is not shown anywhere else

Removed (reference material that the settings pages already state):
  4 Record + alerts
  5 USB disk
  6 Power meter

`help_page` indexes with `page % HELP.len()` and builds the "n/N" title from
that length, so shrinking the array needs no other change.

    python mkpatch7.py FIRMWARE_SRC_DIR
"""

import io
import os
import re
import sys

SRC = sys.argv[1]
PATH = os.path.join(SRC, "ui.rs")

DROP = ("Record + alerts", "USB disk", "Power meter")

DECL7 = "; 8]); 7] = ["
DECL4 = "; 8]); 4] = ["

text = io.open(PATH, encoding="utf-8").read()

i = text.find("pub const HELP: [")
if i < 0:
    sys.exit("HELP declaration not found")
d = text.find(DECL7, i)
if d < 0:
    sys.exit("HELP is not the 7-page table (already patched?)")

start = text.index("[", d)          # the '[' that opens the array body
end = text.index("\n];", start)
body = text[start + 1:end]

# Split the array body into page blocks: each starts with "    (\n" and ends
# with "    ),".
blocks = re.findall(r"\n    \(\n.*?\n    \),", body, re.S)
if len(blocks) != 7:
    sys.exit("parsed %d page blocks, expected 7" % len(blocks))

kept = []
for b in blocks:
    topic = re.search(r'"([^"]+)"', b).group(1)
    if topic in DROP:
        sys.stderr.write("dropped: %s\n" % topic)
    else:
        kept.append(b)
        sys.stderr.write("kept:    %s\n" % topic)

if len(kept) != 4:
    sys.exit("kept %d pages, expected 4" % len(kept))

new_body = "".join(kept) + "\n"
text = text[:start + 1] + new_body + text[end:]
text = text.replace(DECL7, DECL4)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
sys.stderr.write("HELP: 7 -> 4 pages\n")

