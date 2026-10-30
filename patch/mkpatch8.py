#!/usr/bin/env python3
"""The last of the range page and the USB disk values.

Made possible by trimming the help pages (mkpatch7.py), which freed 1,048 B.

  ui.rs    "Wave" (button and its pressed-feedback label) -> 波形
           the range page's "OK"                          -> 确定
           usb_disk_name                                  -> 只读 / 可写 (+重插)
  app.rs   the AUTO+ note line                             -> 自动+ 更安全 ... mV
  dmm.rs   MV_AUTO_WARN (the orange mV warning)            -> 自动 从 mV 起 ...

New glyphs needed: 形 定 只 读 可 写 重 插 安 全 到 降 从 起 (14, about 840 B).

    python mkpatch8.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui.rs": [
        # the Wave button, and the label the pressed-feedback path draws
        ('sf::glyphs(sf::TEXT22, WAVE_BTN, "Wave", STATUS_FG, 0x2966, 8, 0);',
         'sf::glyphs(sf::TEXT22, WAVE_BTN, "\u6ce2\u5f62", STATUS_FG, 0x2966, 8, 0);'),
        ('RP_WAVE => (WAVE_BTN, "Wave", false),',
         'RP_WAVE => (WAVE_BTN, "\u6ce2\u5f62", false),'),
        # the range page's OK button (Hold/Limits was repainted by mkpatch6)
        ('for (x, t) in [(8i16, "\u4fdd\u6301\u9650\u503c"), (319, "OK")] {',
         'for (x, t) in [(8i16, "\u4fdd\u6301\u9650\u503c"), (319, "\u786e\u5b9a")] {'),
        # the USB disk mode: read-only vs writable, and the re-plug hint
        ('        (true, true) => "Files live",\n'
         '        (false, true) => "PC can edit",\n'
         '        (true, false) => "Files live (re-plug)",\n'
         '        (false, false) => "PC can edit (re-plug)",',
         '        (true, true) => "\u53ea\u8bfb",\n'
         '        (false, true) => "\u53ef\u5199",\n'
         '        (true, false) => "\u53ea\u8bfb (\u91cd\u63d2)",\n'
         '        (false, false) => "\u53ef\u5199 (\u91cd\u63d2)",'),
    ],
    "app.rs": [
        ('("AUTO+ recommended: never steps to mV", false)',
         '("\u81ea\u52a8+ \u66f4\u5b89\u5168: \u4e0d\u964d\u5230 mV", false)'),
    ],
    "dmm.rs": [
        ('pub const MV_AUTO_WARN: &str = "AUTO starts on mV: AUTO+ is safer";',
         'pub const MV_AUTO_WARN: &str = "\u81ea\u52a8\u4ece mV \u8d77: \u81ea\u52a8+ \u66f4\u5b89\u5168";'),
    ],
}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            n = text.count(old)
            if n != 1:
                sys.exit("%s: %d occurrences of %r" % (name, n, old[:70]))
            text = text.replace(old, new)
            total += 1
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        sys.stderr.write("%-10s %d replacement(s)\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
