#!/usr/bin/env python3
"""Claim two icon-font blobs for region A2.

Region A2 (zero-wait, below the loader marker) had 1,128 bytes free while
region B sat 60 bytes above its floor. A2 is as fast as B, and these two blobs
are redrawn only when a badge changes, so putting them there is free:

    MODE_B            672 B
    G_08059428_B      150 B

The `.a2` output section is declared before `.text`, and the first matching
rule wins, so listing the input section names there is enough -- stockfont_data.rs
does not have to change.

    python mka2.py FIRMWARE_DIR
"""

import io
import os
import sys

PATH = os.path.join(sys.argv[1], "link-native.x")

ANCHOR = "        *(.rodata.a2 .rodata.a2.*);"
BLOCK = """        *(.rodata.a2 .rodata.a2.*);
        /* zh patch: two icon fonts, redrawn only on a badge change. A2 is
         * zero-wait like B, and B needed the room for Chinese glyphs. */
        *(.rodata.fonts.MODE_B);
        *(.rodata.fonts.G_08059428_B);"""

raw = io.open(PATH, "rb").read()
text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
if text.startswith("\ufeff"):
    text = text[1:]

if "rodata.fonts.MODE_B" in text:
    sys.stderr.write("link-native.x: A2 already patched\n")
else:
    if text.count(ANCHOR) != 1:
        sys.exit("anchor appears %d times" % text.count(ANCHOR))
    text = text.replace(ANCHOR, BLOCK)
    sys.stderr.write("link-native.x: MODE_B + G_08059428_B -> A2\n")

io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
