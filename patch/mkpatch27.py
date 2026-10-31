#!/usr/bin/env python3
"""The green toast a tap on the readout pops up: the rate banner.

`ui::rate_toast` builds "MED 5.0/s" or "MED 5.0/s, +1 digit in 3.2 s" or
"MED 5.0/s, 60000 counts" from dmm::RATE_NAMES. That array must stay ASCII --
app.rs writes it into SCPI replies -- so the toast uses its own table, the same
one the settings page shows (慢 / 中 / 快).

    MED 5.0/s              -> 中 5.0/s
    ", +1 digit in 3.2 s"  -> ", 附加位 3.2 s"
    ", 3.2 s average"      -> ", 平均 3.2 s"
    ", 60000 counts"       -> ", 60000 计数"

    python mkpatch27.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
UI = os.path.join(SRC, "ui.rs")

ui = io.open(UI, encoding="utf-8").read()


def sub(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    return text.replace(old, new)


ui = sub(ui,
         '    put(crate::dmm::RATE_NAMES.get(rate as usize).copied().unwrap_or(""));',
         '    // UI names; dmm::RATE_NAMES stays ASCII for SCPI.\n'
         '    put(["慢", "中", "快"].get(rate as usize).copied().unwrap_or(""));',
         "rate name")

ui = sub(ui, '            put(", +1 digit in ");', '            put(", 附加位 ");', "digit text")
ui = sub(ui, '            put(" s average");', '            put(" s 平均");', "average text")
ui = sub(ui, '        put(", 60000 counts");', '        put(", 60000 计数");', "counts text")

io.open(UI, "w", encoding="utf-8", newline="\n").write(ui)
sys.stderr.write("done: rate toast in Chinese\n")
