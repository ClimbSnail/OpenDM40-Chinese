#!/usr/bin/env python3
"""The last English red toasts.

    "Lowest V/div" / "Highest V/div"   -> 最低 V/div / 最高 V/div
    "Please stop sample"               -> 请先停止采样
    "No record to save"                -> 无波形可保存

    python mkpatch29.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
WAVE = os.path.join(SRC, "app_wave.rs")
SCOPE = os.path.join(SRC, "scope_page.rs")

wave = io.open(WAVE, encoding="utf-8").read()
scope = io.open(SCOPE, encoding="utf-8").read()


def sub(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    return text.replace(old, new)


wave = sub(wave,
           'toast(now, if smaller { "Lowest V/div" } else { "Highest V/div" }, false)',
           'toast(now, if smaller { "最低 V/div" } else { "最高 V/div" }, false)',
           "v/div limits")

scope = sub(scope,
            'toast(now, if self.scope.s.run { "Please stop sample" } else { "No record to save" }, false)',
            'toast(now, if self.scope.s.run { "请先停止采样" } else { "无波形可保存" }, false)',
            "save refusal")

io.open(WAVE, "w", encoding="utf-8", newline="\n").write(wave)
io.open(SCOPE, "w", encoding="utf-8", newline="\n").write(scope)
sys.stderr.write("done: two red toasts in Chinese\n")
