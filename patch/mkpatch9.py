#!/usr/bin/env python3
"""Everything that was still English and is drawn with TEXT22.

TEXT22 is the only font that carries hanzi, so these are the strings that can
become Chinese at all. The F14 / SC_F12 / SC_F16 surfaces (DMM small labels,
scope timebase, popup measurements) stay English: at 12-16 px a hanzi is a
smudge, which was measured on the meter earlier.

Deliberately left alone even though they are TEXT22:
  "A-HOLD"      the badge is 71 px wide; 自动保持 would need 88
  T_LABELS      "PT100" / "NTC10k B3950" are sensor designations, not words
  "Vpp"         a symbol

    python mkpatch9.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

JOBS = {
    "ui.rs": [
        # ---- limits page ---------------------------------------------
        ('''pub const LIMIT_ROWS: [&str; 9] = [
    "Auto Hold", "Limits", "Upper limit", "Lower limit", "Upper = reading", "Lower = reading", "Clear limits",
    "Fail beep", "Record",
];''',
         '''pub const LIMIT_ROWS: [&str; 9] = [
    "\u81ea\u52a8\u4fdd\u6301", "\u9650\u503c", "\u4e0a\u9650", "\u4e0b\u9650",
    "\u4e0a\u9650=\u8bfb\u6570", "\u4e0b\u9650=\u8bfb\u6570", "\u6e05\u9664\u9650\u503c",
    "\u5931\u8d25\u8702\u9e23", "\u8bb0\u5f55",
];'''),
        # ---- record page ---------------------------------------------
        ('pub const RECORD_ROWS: [&str; 4] = ["Interval", "Duration", "Free", ""];',
         'pub const RECORD_ROWS: [&str; 4] = ["\u95f4\u9694", "\u65f6\u957f", "\u53ef\u7528", ""];'),
        ('pub const REC_INTERVALS: [&str; 5] = ["Every reading", "1 s", "10 s", "1 min", "Fast"];',
         'pub const REC_INTERVALS: [&str; 5] = ["\u6bcf\u6b21", "1\u79d2", "10\u79d2", "1\u5206", "\u6700\u5feb"];'),
        ('pub const REC_DURATIONS: [&str; 5] = ["Until stopped", "10 min", "1 h", "8 h", "24 h"];',
         'pub const REC_DURATIONS: [&str; 5] = ["\u624b\u52a8\u505c", "10\u5206", "1\u5c0f\u65f6", "8\u5c0f\u65f6", "24\u5c0f\u65f6"];'),
        # ---- signal generator ---------------------------------------
        ('const GEN_NAMES: [&str; 4] = ["Frequency", "Vpp", "Offset", "Duty"];',
         'const GEN_NAMES: [&str; 4] = ["\u9891\u7387", "Vpp", "\u504f\u79fb", "\u5360\u7a7a"];'),
        # ---- temperature page ---------------------------------------
        ('sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "Temperature Settings", STATUS_FG, 0x2966, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "\u6e29\u5ea6\u8bbe\u7f6e", STATUS_FG, 0x2966, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(8, T_ROW_Y, 118, T_ROW_H), "Offset", STATUS_FG, BG, 1, 0);',
         'sf::glyphs(sf::TEXT22, rect(8, T_ROW_Y, 118, T_ROW_H), "\u504f\u79fb", STATUS_FG, BG, 1, 0);'),
        # ---- page title bar back key --------------------------------
        ('sf::glyphs(sf::TEXT22, rect(BAR_X + 3, 0, 110, PAGE_BAR_H), "< Back", STATUS_FG, 0x2966, 1, 0);',
         'sf::glyphs(sf::TEXT22, rect(BAR_X + 3, 0, 110, PAGE_BAR_H), "< \u8fd4\u56de", STATUS_FG, 0x2966, 1, 0);'),
    ],
    # ---- inrush page -------------------------------------------------
    "ui_inrush.rs": [
        ('const BOX_NAME: [&str; 2] = ["Irms 100 ms", "Peak"];',
         'const BOX_NAME: [&str; 2] = ["\u6709\u6548\u503c100ms", "\u5cf0\u503c"];'),
        ('sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "Inrush Current", STATUS_FG, BTN, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "\u6d8c\u6d41", STATUS_FG, BTN, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, THR_LABEL, "Trigger", STATUS_FG, BG, 1, 0);',
         'sf::glyphs(sf::TEXT22, THR_LABEL, "\u89e6\u53d1", STATUS_FG, BG, 1, 0);'),
        ('sf::glyphs(sf::TEXT22, BACK_BTN, "Back", STATUS_FG, BTN, 8, 0);',
         'sf::glyphs(sf::TEXT22, BACK_BTN, "\u8fd4\u56de", STATUS_FG, BTN, 8, 0);'),
    ],
    # ---- power meter pages -------------------------------------------
    "ui_power.rs": [
        ('sf::glyphs(sf::TEXT22, rect(x, y, w, 34), "Power meter: wiring", STATUS_FG, DLG_TITLE, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(x, y, w, 34), "\u529f\u7387\u8ba1\u63a5\u7ebf", STATUS_FG, DLG_TITLE, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "Power Settings", STATUS_FG, 0x2966, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(0, 0, 480, 40), "\u529f\u7387\u8bbe\u7f6e", STATUS_FG, 0x2966, 8, 0);'),
    ],
    # ---- gallery -----------------------------------------------------
    "gallery.rs": [
        ('sf::glyphs(sf::TEXT22, rect(BACK_X, 0, 110, BAR_H), "< Back", FG, BAR, 1, 0);',
         'sf::glyphs(sf::TEXT22, rect(BACK_X, 0, 110, BAR_H), "< \u8fd4\u56de", FG, BAR, 1, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(0, 0, 480, BAR_H), "Gallery", FG, BAR, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(0, 0, 480, BAR_H), "\u56fe\u5e93", FG, BAR, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(px, py, pw, ph), "No data", DIM, PANEL, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(px, py, pw, ph), "\u65e0\u6570\u636e", DIM, PANEL, 8, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(DEL.0, DEL.1, DEL.2, DEL.3), "Delete", FG, D_RED, 8, 0);',
         'sf::glyphs(sf::TEXT22, rect(DEL.0, DEL.1, DEL.2, DEL.3), "\u5220\u9664", FG, D_RED, 8, 0);'),
    ],
    # ---- touch test legend -------------------------------------------
    "ui_touchtest.rs": [
        ('sf::glyphs(sf::TEXT22, rect(LINE_X + 74, LEGEND_Y, 100, 20), "corrected", STATUS_FG, M_BG, 1, 0);',
         'sf::glyphs(sf::TEXT22, rect(LINE_X + 74, LEGEND_Y, 100, 20), "\u6821\u6b63", STATUS_FG, M_BG, 1, 0);'),
        ('sf::glyphs(sf::TEXT22, rect(LINE_X + 203, LEGEND_Y, 60, 20), "down", STATUS_FG, M_BG, 1, 0);',
         'sf::glyphs(sf::TEXT22, rect(LINE_X + 203, LEGEND_Y, 60, 20), "\u4e0b\u6ed1", STATUS_FG, M_BG, 1, 0);'),
    ],
    # ---- scope menu tabs (SC_F22 is TEXT22) --------------------------
    "scope_ui.rs": [
        ('pub const MF_TABS: [&str; 4] = ["Measure", "Display", "Trigger", "Settings"];',
         'pub const MF_TABS: [&str; 4] = ["\u6d4b\u91cf", "\u663e\u793a", "\u89e6\u53d1", "\u8bbe\u7f6e"];'),
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
        sys.stderr.write("%-16s %d replacement(s)\n" % (name, len(reps)))
    sys.stderr.write("total %d\n" % total)


main()
