#!/usr/bin/env python3
"""Draw the Chinese strings with TEXT22 -- the only font that has hanzi.

`check_fonts.py` finds 19 lines where a translated literal is drawn with a
stock font (ASCII26, SC_F16, F14, ...). Those tables are ASCII only (their
highest code point is 0x2109), so the hanzi come out blank on the panel and
the build says nothing: the literal is still valid UTF-8.

v0.4.0-zh hit the same wall and switched the call sites to TEXT22 instead of
adding glyphs to F14 (12 px line spacing cannot hold a 14 px hanzi; see
patch/legacy-v030/SCOPE.md). This script does the same for v0.4.1.

    font_fix.py --src firmware/src [--dry-run]

Two line-level edits:
  * `ui_power.rs`'s two 14 px boxes grow to 18 px (and move up 2 px) so the
    22 px TEXT22 cell is not clipped -- the tall rect of every other site is
    already >= 22, and a hanzi glyph's first ink row is ~3, so the rest need
    nothing;
  * every other flagged line keeps its layout and only swaps the font token.

Idempotent: a line that already says `sf::TEXT22` is left alone.
"""

import argparse
import io
import os
import re
import sys

CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
FONTS = "ASCII26|TEXT22|SC_F16|SC_F12|SC_F20|F14|F78|F21|UNIT|LETTERS|K_FONT|HIST|ICONS"
FONT_RE = re.compile(r"\b(" + FONTS + r")\b")

# Font + rect on one line: TEXT22 is 22 px per line, these boxes were 14.
EXPLICIT = [
    ("ui_power.rs",
     'sf::glyphs(sf::F14, rect(426, y + 4, 46, 14), if pv.run { "运行" } else { "暂停" }',
     'sf::glyphs(sf::TEXT22, rect(426, y + 2, 46, 18), if pv.run { "运行" } else { "暂停" }'),
    ("ui_power.rs",
     'sf::label(sf::F14, rect(SHUNT.x + SHUNT.w + 4, SHUNT.y + 7, 44, 14), "分流"',
     'sf::label(sf::TEXT22, rect(SHUNT.x + SHUNT.w + 4, SHUNT.y + 5, 44, 18), "分流"'),
    # The chip used the scope's 26 px face only because "BEEP" needs B and E;
    # the Chinese alternative needs a face with hanzi, and TEXT22 has both.
    ("ui.rs",
     "            // The scope's 26 px face (the status bar's F21 lacks B / E).\n"
     '            sf::glyphs(sf::ASCII26, b,',
     "            // TEXT22: the only face with hanzi (the status bar's F21 lacks\n"
     "            // B / E, ASCII26 lacks 短路).\n"
     '            sf::glyphs(sf::TEXT22, b,'),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    explicit = {}
    for f, old, new in EXPLICIT:
        explicit.setdefault(f, []).append((old, new))

    changed = []
    for f, pairs in explicit.items():
        path = os.path.join(a.src, f)
        t = io.open(path, encoding="utf-8").read()
        for old, new in pairs:
            if new in t:
                continue
            n = t.count(old)
            if n != 1:
                sys.exit("%s: expected 1 hit, found %d -- upstream changed" % (f, n))
            t = t.replace(old, new)
            changed.append((f, "rect+font"))
        if not a.dry_run:
            io.open(path, "w", encoding="utf-8", newline="\n").write(t)

    # Everything else: swap the font token on the flagged lines only.
    for dirpath, _, files in os.walk(a.src):
        for f in sorted(files):
            if not f.endswith(".rs"):
                continue
            path = os.path.join(dirpath, f)
            lines = io.open(path, encoding="utf-8").read().split("\n")
            hit = False
            for i, line in enumerate(lines):
                if line.lstrip().startswith("//") or not CJK.search(line):
                    continue
                if "TEXT22" in line:
                    continue
                m = FONT_RE.search(line)
                if not m:
                    continue
                lines[i] = line[:m.start(1)] + "TEXT22" + line[m.end(1):]
                changed.append((f, "font"))
                hit = True
            if hit and not a.dry_run:
                io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))

    print("%d edit(s)%s" % (len(changed), " [dry run]" if a.dry_run else ""))
    per = {}
    for f, kind in changed:
        per[f] = per.get(f, 0) + 1
    for f in sorted(per):
        print("   %-14s %d" % (f, per[f]))


if __name__ == "__main__":
    main()
