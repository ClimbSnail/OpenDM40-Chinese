#!/usr/bin/env python3
"""Move five more glyph blobs into region A2.

Dropping ASCII26 (mkpatch17) left A2 with 6,584 bytes free. A2 is zero-wait,
the same speed as B, so anything read-only that is redrawn only on a screen
change can live there.

    K_FONT      2,080 B   the keypad's digits
    ICONS       1,136 B   the menu tiles' icons
    BTN_GLYPH     952 B   function-button glyphs
    BATTERY       771 B   the battery icon
    LIGHTNING     276 B   the alert icon
                 -----
                 5,215 B freed in region B, which had 316 B to spare

    python mka22.py FIRMWARE_DIR
"""

import io
import os
import sys

PATH = os.path.join(sys.argv[1], "link-native.x")

ANCHOR = "        *(.rodata.fonts.MODE_B);"
BLOCK = """        *(.rodata.fonts.MODE_B);
        /* zh patch: the rest of the room ASCII26 gave back. All of these are
         * redrawn only when a screen changes, and A2 is as fast as B. */
        *(.rodata.fonts.K_FONT_B);
        *(.rodata.fonts.ICONS_B);
        *(.rodata.fonts.BTN_GLYPH_B);
        *(.rodata.fonts.BATTERY_B);
        *(.rodata.fonts.LIGHTNING_B);"""

raw = io.open(PATH, "rb").read()
text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
if text.startswith("\ufeff"):
    text = text[1:]

if "rodata.fonts.K_FONT_B" in text:
    sys.stderr.write("link-native.x: A2 already extended\n")
else:
    if text.count(ANCHOR) != 1:
        sys.exit("anchor appears %d times" % text.count(ANCHOR))
    text = text.replace(ANCHOR, BLOCK)
    sys.stderr.write("link-native.x: +5 blobs -> A2\n")

io.open(PATH, "w", encoding="utf-8", newline="\n").write(text)
