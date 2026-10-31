#!/usr/bin/env python3
"""Dialog bodies, dialog titles and the power page's remaining buttons.

Region B now has 13,724 B (5,532 usable) after five more glyph blobs moved to
A2, so the long dialog sentences finally fit.

Dialogs are drawn with TEXT22 since mkpatch17, so a hanzi costs 64 B.

  fuse_check bodies and titles (ui.rs)
      "Lead from V/ohm jack to A"   -> 表笔从 V/Ω 插孔接到 A
      "nothing else connected"      -> 其他不要接
      "Measuring ..."               -> 测量中 ...
      "expect ~48 ohm"              -> 应约 48 欧
      "A input path intact"         -> A 通道完好
      "OL: no path from V to A"     -> OL: V 到 A 不通
      "Replace: 10 A ceramic fuse"  -> 更换 10A 陶瓷保险丝
      "One lead V/ohm to A only"    -> 只用一根表笔接 A
      "No ohm reading"              -> 无电阻读数
      "Check leads"                 -> 检查表笔
      "FUSE OK" / "FUSE OPEN"       -> 保险丝正常 / 保险丝已断
      "OK" (the dialog's right key) -> 确定

  power page (ui_power.rs)
      "At load"  -> 带载
      "Wiring"   -> 接线
      "Reset Wh" -> 复位电能
      "Power meter: wiring" -> 功率计接线

    python mkpatch20.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui.rs": [
        ('"Lead from V/ohm jack to A", "nothing else connected"',
         '"\u8868\u7b14\u4ece V/\u03a9 \u63d2\u5b54\u63a5\u5230 A", "\u5176\u4ed6\u4e0d\u8981\u63a5"'),
        ('"Measuring ...", "expect ~48 ohm"',
         '"\u6d4b\u91cf\u4e2d ...", "\u5e94\u7ea6 48 \u6b27"'),
        ('"FUSE OK"', '"\u4fdd\u9669\u4e1d\u6b63\u5e38"'),
        ('"A input path intact"', '"A \u901a\u9053\u5b8c\u597d"'),
        ('"FUSE OPEN"', '"\u4fdd\u9669\u4e1d\u5df2\u65ad"'),
        ('"OL: no path from V to A", "Replace: 10 A ceramic fuse"',
         '"OL: V \u5230 A \u4e0d\u901a", "\u66f4\u6362 10A \u9676\u74f7\u4fdd\u9669\u4e1d"'),
        ('"Check leads"', '"\u68c0\u67e5\u8868\u7b14"'),
        ('"One lead V/ohm to A only"', '"\u53ea\u7528\u4e00\u6839\u8868\u7b14\u63a5 A"'),
        ('"No ohm reading"', '"\u65e0\u7535\u963b\u8bfb\u6570"'),
        ('Some("OK")', 'Some("\u786e\u5b9a")'),
    ],
    "ui_power.rs": [
        ('ps_button(ps_cell(2, 2), "At load", pv.comp);',
         'ps_button(ps_cell(2, 2), "\u5e26\u8f7d", pv.comp);'),
        ('(PS_RESET, "Reset Wh")', '(PS_RESET, "\u590d\u4f4d\u7535\u80fd")'),
        ('(PS_WIRING, "Wiring")', '(PS_WIRING, "\u63a5\u7ebf")'),
        ('"\u529f\u7387\u8bbe\u7f6e", STATUS_FG, 0x2966, 8, 0);', '"\u529f\u7387\u8bbe\u7f6e", STATUS_FG, 0x2966, 8, 0);'),
    ],
}


def main():
    total = 0
    for name, reps in JOBS.items():
        path = os.path.join(SRC, name)
        text = io.open(path, encoding="utf-8").read()
        for old, new in reps:
            if old == new:
                continue
            n = text.count(old)
            if n == 0:
                sys.stderr.write("%-12s MISS %r\n" % (name, old[:50]))
                continue
            text = text.replace(old, new)
            total += n
            sys.stderr.write("%-12s %-46r x%d\n" % (name, old[:44], n))
        io.open(path, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("total %d\n" % total)


main()
