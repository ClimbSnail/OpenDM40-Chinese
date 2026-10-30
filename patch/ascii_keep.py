#!/usr/bin/env python3
"""Work out the smallest ASCII set TEXT22 actually needs, and report it.

TEXT22 carries 92 ASCII glyphs at roughly 45-50 B each -- about 4 KB of a
region B that has 332 B spare. Most of that ASCII never reaches a TEXT22 line
any more now that the labels are Chinese; what is left is numbers and units
built at run time, plus a handful of English words that stay on purpose
("OPEN", "A-JACK", "PT100", the sensor model names).

The set is derived, not guessed:

  * every literal that a TEXT22 draw call uses, directly or through one of the
    string tables that `list_page` / `record_page` / a chip prints;
  * plus RUNTIME, the alphabet the value formatters can emit (digits, sign,
    decimal point, the unit letters, the separator the UI puts between value
    and unit).

Anything outside the union is reported as droppable, and the meter is checked
screen by screen afterwards -- a wrong prune shows up as a blank box.

    python ascii_keep.py SRC_DIR OUTFILE
"""

import io
import os
import re
import sys

SRC, OUT = sys.argv[1], sys.argv[2]

LIT = re.compile(r'"((?:[^"\\]|\\.)*)"')
TEXT22_CALL = re.compile(r"sf::(?:glyphs|label|text)\(\s*sf::TEXT22")

# Tables that end up inside a TEXT22 draw (list_page, record_page, chips,
# page titles, toasts, scope tabs -- SC_F22 is an alias of TEXT22).
TABLES = {
    "SETTINGS", "SETTINGS2", "SETTINGS3", "TILES", "LIMIT_ROWS", "RECORD_ROWS",
    "REC_INTERVALS", "REC_DURATIONS", "T_LABELS", "T_KEYS", "GEN_NAMES",
    "BOX_NAME", "CPL_NAMES", "OHM_VARS", "KEY_NAMES", "MF_TABS", "HELP",
    "RATE_TXT", "DIM_TXT", "OFF_TXT", "SMOOTH_NAMES", "DRAG_NAMES", "TAP_NAMES",
}

# What the value formatters can put on a TEXT22 line at run time.
RUNTIME = set(
    "0123456789"
    " .-+/,:()%<>="
    "VAmWHzsnukMGCFPKTNBJOLISUDRE"
    "dhpez"
    "\u00b0\u03a9"
)

used = set(RUNTIME)

for name in sorted(os.listdir(SRC)):
    if not name.endswith(".rs"):
        continue
    text = io.open(os.path.join(SRC, name), encoding="utf-8").read()
    text = re.sub(r"//[^\n]*", "", text)
    lines = text.split("\n")

    for line in lines:
        if TEXT22_CALL.search(line):
            for m in LIT.finditer(line):
                used |= set(m.group(1))

    for m in re.finditer(r"const\s+(\w+)\s*:\s*\[&str;\s*\d+\]\s*=\s*\[(.*?)\];", text, re.S):
        if m.group(1) in TABLES:
            for lit in LIT.findall(m.group(2)):
                used |= set(lit)

# HELP is an array of tuples, so the regex above misses it; pull its strings in
# explicitly when the table survives.
h = re.search(r"pub const HELP: \[(&str, \[\(&str, &str\); 8\)); (\d+)\] = \[(.*?)\n\];", text, re.S) \
    if "pub const HELP: [" in text else None
if h:
    for lit in LIT.findall(h.group(3)):
        used |= set(lit)

ascii_keep = sorted(c for c in used if 0x20 <= ord(c) < 0x7F)
full = [chr(c) for c in range(0x20, 0x7F)]
dead = [c for c in full if c not in ascii_keep]

io.open(OUT, "w", encoding="utf-8", newline="\n").write("".join(ascii_keep))
print("keep %d ASCII: %r" % (len(ascii_keep), "".join(ascii_keep)))
print("drop %d ASCII: %r   (~%d B)" % (len(dead), "".join(dead), len(dead) * 46))
