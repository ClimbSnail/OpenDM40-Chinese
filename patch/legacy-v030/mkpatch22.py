#!/usr/bin/env python3
"""Remove the help page: the Settings row, its handler and its text.

The help page was down to one page with four English rows -- mostly a marker
for operations the manual covers anyway. Removing it:

  ui.rs   SETTINGS2 loses its "帮助" row (9 -> 8 entries)
  app.rs  the page-1 value array loses the Help row; row 8 (More) becomes 7,
          and the "Some(7) => open Help" arm goes
  ui.rs   the four remaining English rows become empty strings

`View::Help` and `ui::help_page()` stay in place (unreachable) so nothing else
has to change; only the text and the entry point go.

    python mkpatch22.py FIRMWARE_SRC_DIR
"""

import io
import os
import re
import sys

SRC = sys.argv[1]

UI = os.path.join(SRC, "ui.rs")
APP = os.path.join(SRC, "app.rs")

# ---- 1. SETTINGS2: drop the help row --------------------------------
ui = io.open(UI, encoding="utf-8").read()

m = re.search(r"pub const SETTINGS2: \[&str; 9\] = \[(.*?)\];", ui, re.S)
if not m:
    sys.exit("SETTINGS2 not found")
items = re.findall(r'"([^"]*)"', m.group(1))
if len(items) != 9:
    sys.exit("SETTINGS2 has %d entries, expected 9" % len(items))

kept = [x for x in items if x not in ("帮助", "Help")]
if len(kept) != 8:
    sys.exit("dropped %d entries, expected 1" % (9 - len(kept)))

body = "\n" + "".join('    "%s",\n' % x for x in kept)
ui = ui[:m.start()] + "pub const SETTINGS2: [&str; 8] = [" + body + "];" + ui[m.end():]
sys.stderr.write("ui.rs: SETTINGS2 9 -> 8 rows\n")

# ---- 2. empty the help text -----------------------------------------
h = re.search(r'(\n    \(\n        "Gestures",\n        \[\n)(.*?)(\n        \],\n    \),)', ui, re.S)
if not h:
    sys.exit("Gestures block not found")
ui = ui[:h.start(2)] + "\n" + "\n".join(['            ("", ""),'] * 8) + ui[h.end(2):]
sys.stderr.write("ui.rs: help rows cleared\n")

io.open(UI, "w", encoding="utf-8", newline="\n").write(ui)

# ---- 3. app.rs: values array and the press arms ---------------------
app = io.open(APP, encoding="utf-8").read()

old_vals = '                    "", // Help row: opens the help pages (UF-29)\n'
if app.count(old_vals) != 1:
    sys.exit("help row comment not found (%d)" % app.count(old_vals))
app = app.replace(old_vals, "")

old_arm = """                    Some(7) => {
                        self.help_page = 0;
                        self.show(View::Help, clk);
                        return;
                    }
                    Some(8) => self.set_page = 2,"""
new_arm = """                    Some(7) => self.set_page = 2,"""
if app.count(old_arm) != 1:
    sys.exit("press arms not found (%d)" % app.count(old_arm))
app = app.replace(old_arm, new_arm)

io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("app.rs: help row + arm removed, More 8 -> 7\n")
