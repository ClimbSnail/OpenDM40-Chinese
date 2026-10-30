#!/usr/bin/env python3
"""Settings VALUES and the range page: the second round of Chinese.

Everything here is drawn with TEXT22 (the 22 px font that carries hanzi), so
it can be Chinese. `list_page` gives the value column 250 px, far more than a
2-4 character hanzi string needs.

Every replacement must occur exactly once; a miss aborts with the offending
snippet, so an upstream change fails loudly instead of patching the wrong
thing.

    python mkpatch4.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    # ---- settings page 1: Dim screen / Shutdown durations -------------
    "app.rs": [
        ('const DIM_TXT: [&str; 4] = ["5 min", "10 min", "30 min", "Never"];',
         'const DIM_TXT: [&str; 4] = ["5\u5206", "10\u5206", "30\u5206", "\u6c38\u4e0d"];'),
        ('const OFF_TXT: [&str; 4] = ["10 min", "30 min", "1 hour", "Never"];',
         'const OFF_TXT: [&str; 4] = ["10\u5206", "30\u5206", "1\u5c0f\u65f6", "\u6c38\u4e0d"];'),
        # ---- page 3: the jack-alert mask ------------------------------
        ('        M_JACK => "ON",\n        M_AJACK => "A-JACK only",\n        0 => "OFF",',
         '        M_JACK => "\u5f00",\n        M_AJACK => "\u4ec5 A-JACK",\n        0 => "\u5173",'),
        # ---- page 2: DMM row, temperature unit, scope swipe, scope press
        ('if self.dmm_view.bar_on { "Bargraph" } else { "History" }',
         'if self.dmm_view.bar_on { "\u67f1\u72b6\u56fe" } else { "\u5386\u53f2" }'),
        ('if self.dmm.temp_f() { "F (Fahrenheit)" } else { "C (Celsius)" }',
         'if self.dmm.temp_f() { "\u534e\u6c0f" } else { "\u6444\u6c0f" }'),
        ('if self.sp.swipes { "Top bar" } else { "Off (stock)" }',
         'if self.sp.swipes { "\u9876\u680f" } else { "\u5173 (\u539f\u5382)" }'),
        ('if self.sp.press_fx { "ON" } else { "OFF (stock)" }',
         'if self.sp.press_fx { "\u5f00" } else { "\u5173 (\u539f\u5382)" }'),
        # ---- page 3: burden voltage -----------------------------------
        ('if self.dmm.burden_show { "ON (A, mA, uA)" } else { "OFF (stock)" }',
         'if self.dmm.burden_show { "\u5f00 (A, mA, uA)" } else { "\u5173 (\u539f\u5382)" }'),
        # ---- page 1: analog power -------------------------------------
        ('if self.rails_both { "Both always" } else { "Auto (per view)" }',
         'if self.rails_both { "\u4e24\u8005\u5e38\u5f00" } else { "\u81ea\u52a8 (\u6309\u89c6\u56fe)" }'),
        # ---- page 1: Bluetooth, page 3: accuracy, negative ohm --------
        ('if self.bt_on { "ON" } else { "OFF" },',
         'if self.bt_on { "\u5f00" } else { "\u5173" },'),
        ('if self.dmm_view.acc_on { "ON" } else { "OFF" },',
         'if self.dmm_view.acc_on { "\u5f00" } else { "\u5173" },'),
        ('if self.dmm.ohm_neg { "ON" } else { "OFF (stock)" },',
         'if self.dmm.ohm_neg { "\u5f00" } else { "\u5173 (\u539f\u5382)" },'),
    ],
    # ---- page 2: smoothing --------------------------------------------
    "meter.rs": [
        ('pub const SMOOTH_NAMES: [&str; 3] = ["OFF", "LOW", "HIGH"];',
         'pub const SMOOTH_NAMES: [&str; 3] = ["\u5173", "\u4f4e", "\u9ad8"];'),
    ],
    # ---- page 2: scope tap step ---------------------------------------
    "scope_ui.rs": [
        ('pub const TAP_NAMES: [&str; 3] = ["Halves (stock)", "Corners", "Off"];',
         'pub const TAP_NAMES: [&str; 3] = ["\u5de6\u53f3 (\u539f\u5382)", "\u8fb9\u89d2", "\u5173"];'),
    ],
    # ---- page 1: scope drag -------------------------------------------
    "scope_page.rs": [
        ('pub const DRAG_NAMES: [&str; 2] = ["Stock", "Axis lock"];',
         'pub const DRAG_NAMES: [&str; 2] = ["\u539f\u5382", "\u8f74\u9501\u5b9a"];'),
    ],
    # ---- the range page's buttons -------------------------------------
    "ui.rs": [
        ('sf::glyphs(sf::TEXT22, r, "Fuse check", STATUS_FG, 0x2966, 8, 0);',
         'sf::glyphs(sf::TEXT22, r, "\u4fdd\u9669\u4e1d\u81ea\u68c0", STATUS_FG, 0x2966, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, INRUSH_BTN, "Inrush", STATUS_FG, 0x2966, 8, 0);',
         'sf::glyphs(sf::TEXT22, INRUSH_BTN, "\u6d8c\u6d41", STATUS_FG, 0x2966, 8, 0);'),
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
        sys.stderr.write("%-14s %d replacement(s)\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
