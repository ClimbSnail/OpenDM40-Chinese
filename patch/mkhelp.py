#!/usr/bin/env python3
"""Keep only the help pages named on the command line.

The help text is the last sizable block of English in region B (~350 B per
page) and it stays English no matter what, because translating its 64 rows
would need about 9 KB. Trading pages for Chinese on the screens people
actually look at is the only way to fund the remaining labels.

The page count in the title ("Help n/N") comes from HELP.len(), so nothing
else has to change.

    python mkhelp.py FIRMWARE_SRC_DIR Gestures "Side keys"
"""

import io
import os
import re
import sys

SRC = sys.argv[1]
KEEP = set(sys.argv[2:])
PATH = os.path.join(SRC, "ui.rs")

text = io.open(PATH, encoding="utf-8").read()

m = re.search(r"pub const HELP: \[\(&str, \[\(&str, &str\); 8\]\); (\d+)\] = \[", text)
if not m:
    sys.exit("HELP declaration not found")
n = int(m.group(1))
start = m.end() - 1
end = text.index("\n];", start)
body = text[start + 1:end]

blocks = re.findall(r"\n    \(\n.*?\n    \),", body, re.S)
if len(blocks) != n:
    sys.exit("parsed %d blocks, declaration says %d" % (len(blocks), n))

kept = []
for b in blocks:
    topic = re.search(r'"([^"]+)"', b).group(1)
    if topic in KEEP:
        kept.append(b)
        sys.stderr.write("keep   %s\n" % topic)
    else:
        sys.stderr.write("drop   %s\n" % topic)

if len(kept) != len(KEEP):
    sys.exit("kept %d, expected %d (name mismatch?)" % (len(kept), len(KEEP)))

text = text[:start + 1] + "".join(kept) + "\n" + text[end:]
text = text.replace("(&str, [(&str, &str); 8]); %d]" % n,
                    "(&str, [(&str, &str); 8]); %d]" % len(kept), 1)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
sys.stderr.write("HELP: %d -> %d pages\n" % (n, len(kept)))
