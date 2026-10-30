#!/usr/bin/env python3
"""Move two rarely redrawn glyph blobs into region C, and check the encoding.

Region B holds the zero-wait flash and the project fails the link below 8 KiB
free. The Chinese glyphs eat most of that headroom, so two icon/badge fonts
that are redrawn only when the screen changes are pushed to the slow region:

    HIST_B      the history row's digits            (382 B)
    SAVE_BT_B   the "saved" badge                   (246 B)

Together 628 B, which is what region C can give up: C also has a 4 KiB floor
and only ~640 B to spare.

Rewritten byte-exactly: rust-lld rejects a BOM, and CRLF trips it too, so the
file is normalised to UTF-8 without BOM and LF.

    python mklink.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

FIRMWARE = sys.argv[1]
PATH = os.path.join(FIRMWARE, "link-native.x")

ANCHOR = "        __cold_start = .;"
BLOCK = """        __cold_start = .;
        /* zh patch: glyph blobs that are redrawn only on a screen change,
         * moved out of region B so it stays above its 8 KiB floor now that
         * TEXT22 carries the Chinese glyphs. Region C has room for these. */
        *(.rodata.fonts.HIST_B);
        *(.rodata.fonts.SAVE_BT_B);
"""

raw = io.open(PATH, "rb").read()
text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
if text.startswith("\ufeff"):
    text = text[1:]

if "rodata.fonts.HIST_B" in text:
    sys.stderr.write("link-native.x: already patched\n")
else:
    if text.count(ANCHOR) != 1:
        sys.exit("anchor __cold_start appears %d times" % text.count(ANCHOR))
    text = text.replace(ANCHOR, BLOCK)
    sys.stderr.write("link-native.x: HIST_B + SAVE_BT_B -> region C\n")

io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
