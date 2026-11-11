#!/usr/bin/env python3
"""Finish the Scope / menu localisation that the dictionary pass cannot do.

`apply_dict.py` replaces whole string literals globally. Three groups of
labels were left behind by that pass:

  1. Short generic words (`On`, `Band`, `Power`, `Log`, the colour names, ...)
     cannot go into `zh_dict.csv`: one English literal is used both as a UI
     label and as an SCPI / log / file token, so a global replace would break
     those. They are replaced here by exact, uniquely-matched anchors instead.
  2. Arrays of literals (`MEAS_NAMES`, `WINDOWS`, `COLOUR_NAMES`,
     `TSRC_NAMES`) are display-only, but their members are also short generic
     words. Same reason: anchors here, not dictionary rows.
  3. Translations that *are* in the dictionary (MF tabs, "滚动：", "耦合",
     "探头", the decode page's labels, ...) were still blank on the panel:
     `option_list`, `spinner`, `side_popup` and friends hard-code a stock
     ASCII face inside the helper, while the Chinese literal sits at the call
     site. `check_fonts.py` is line-based and cannot see that pairing, so
     `font_fix.py` never touched them.

     `Ink::new` now picks the face by content: ASCII keeps the stock look,
     anything else goes to `TEXT22` (the only face with hanzi). That covers
     every helper at once. The explicit draw sites are switched to `TEXT22`
     too, so `check_fonts.py` stays clean.

Run after `apply_dict.py` / `font_fix.py` / `dialog_font.py`, before
`derive_sets.py` (the new hanzi have to be in `need_glyphs.txt`):

    scope_zh.py --src build/worktree/firmware/src [--dry-run]

Idempotent: an edit whose result is already in the file is skipped; an anchor
whose hit count changed fails loudly instead of silently dropping a label.
"""

import argparse
import io
import os
import sys

# (file, old, new, expected number of hits)
PATCHES = [
    # ------------------------------------------------------------------ fonts
    ("stockfont.rs",
     "    pub fn new(font: Font, r: Rect, text: &str, align: u8, spacing: i8) -> Ink {\n"
     "        let mut k = Ink::none();",
     "    pub fn new(font: Font, r: Rect, text: &str, align: u8, spacing: i8) -> Ink {\n"
     "        // Only TEXT22 carries the hanzi this project adds. Some callers\n"
     "        // draw a translated literal through a stock ASCII face chosen\n"
     "        // inside a helper (option_list, spinner, side_popup, ...), which\n"
     "        // the line-based font checker cannot see. Pick the face here so\n"
     "        // every one of those strings shows up; ASCII keeps its stock face.\n"
     "        let font = if text.is_ascii() { font } else { TEXT22 };\n"
     "        let mut k = Ink::none();", 1),

    ("scope_ui.rs",
     "    let font = if MF_TABS.iter().all(|t| sf::text_width(sf::SC_F22, t, 0) + 6 <= MF_TAB_W - 1) { sf::SC_F22 } else { sf::SC_F16 };",
     "    // The five tabs are Chinese; SC_F16 has no hanzi. SC_F22 is TEXT22's\n"
     "    // alias, so both branches of the stock width test can draw them.\n"
     "    let font = if MF_TABS.iter().all(|t| sf::text_width(sf::SC_F22, t, 0) + 6 <= MF_TAB_W - 1) { sf::SC_F22 } else { sf::TEXT22 };", 1),
    ("scope_ui.rs",
     "                rbox_text(r, pc, 8, c, C_POP_BG, sf::SC_F16, MEAS_NAMES[i as usize], C_WHITE);",
     "                rbox_text(r, pc, 8, c, C_POP_BG, sf::TEXT22, MEAS_NAMES[i as usize], C_WHITE);", 1),
    ("scope_ui.rs",
     "                rbox_text(r, pc, 8, C_BAR, C_POP_BG, sf::SC_F16, MEAS_NAMES[v.meas[k] as usize % 20], C_YELLOW);",
     "                rbox_text(r, pc, 8, C_BAR, C_POP_BG, sf::TEXT22, MEAS_NAMES[v.meas[k] as usize % 20], C_YELLOW);", 1),
    ("scope_ui.rs",
     "                fill_text(r, pc, C_POP_BG, sf::SC_F16, r, t, C_FILL, 1, 0);",
     "                fill_text(r, pc, C_POP_BG, sf::TEXT22, r, t, C_FILL, 1, 0);", 1),

    # --------------------------------------------------------------- measure tab
    ("scope_ui.rs",
     'pub const MEAS_NAMES: [&str; 20] =\n'
     '    ["Freq", "+Duty", "-Duty", "+Wid", "-Wid", "+Pul", "-Pul", "X2-1", "Xf", "Cycl", "Vp-p", "Vrms", "Vmax", "Vmin", "Vtop", "Vbas", "Vamp", "Y2-1", "Vcrm", "Vavg"];',
     'pub const MEAS_NAMES: [&str; 20] =\n'
     '    ["频率", "占空+", "占空-", "宽+", "宽-", "脉+", "脉-", "X2-1", "Xf", "周期", "峰峰", "有效", "最大", "最小", "顶值", "底值", "幅值", "Y2-1", "均值", "平均"];', 1),

    # --------------------------------------------------------------- display tab
    ("scope_ui.rs", '&["On", "关"]', '&["开", "关"]', 3),
    ("scope_ui.rs", '&["关", "MIN", "1S", "INF"]', '&["关", "最小", "1秒", "无限"]', 1),
    ("scope_ui.rs",
     '            fill_text(C2_LABEL, pc, C_POP_BG, sf::SC_F16, C2_LABEL, "CH2 (DMM):", C_FILL, 1, 0);',
     '            fill_text(C2_LABEL, pc, C_POP_BG, sf::TEXT22, C2_LABEL, "CH2（电表）：", C_FILL, 1, 0);', 1),

    # --------------------------------------------------------------- trigger tab
    ("scope_ui.rs",
     '                    fill_text(TP_LABEL, pc, C_POP_BG, sf::SC_F16, TP_LABEL, "2nd level:", C_FILL, 1, 0);',
     '                    fill_text(TP_LABEL, pc, C_POP_BG, sf::TEXT22, TP_LABEL, "第二电平：", C_FILL, 1, 0);', 1),
    ("scope_ui.rs",
     "pub const TR_HINT: Rect = rect(214, 164, 189, 18);",
     "pub const TR_HINT: Rect = rect(214, 164, 189, 22);", 1),
    ("scope_ui.rs",
     '                    fill_text(TR_HINT, pc, C_POP_BG, sf::SC_F16, TR_HINT, "drag orange T", C_FILL, 1, 0);',
     '                    fill_text(TR_HINT, pc, C_POP_BG, sf::TEXT22, TR_HINT, "拖动橙色 T", C_FILL, 1, 0);', 1),
    ("scope_ui.rs",
     '                fill_text(TS_NOTE, pc, C_POP_BG, sf::SC_F16, TS_NOTE, "edge, computed", C_FILL, 1, 0);',
     '                fill_text(TS_NOTE, pc, C_POP_BG, sf::TEXT22, TS_NOTE, "边沿，计算值", C_FILL, 1, 0);', 1),

    # ------------------------------------------------------------ CH1 / Math popups
    ("scope_ui.rs",
     'pub const COLOUR_NAMES: [&str; 9] = ["red", "orange", "yellow", "green", "blue", "purple", "brown", "pink", "gold"];',
     'pub const COLOUR_NAMES: [&str; 9] = ["红", "橙", "黄", "绿", "蓝", "紫", "棕", "粉", "金"];', 1),
    ("scope_ui.rs",
     '            fill_text(r, pc, C_POP_BG, sf::SC_F16, r, "Scale", C_BAR, 8, 0);',
     '            fill_text(r, pc, C_POP_BG, sf::TEXT22, r, "倍率", C_BAR, 8, 0);', 1),
    ("scope_ui.rs",
     '    side_popup("运算", &["模式", "颜色", "Hz/Div", "其他"], tab);',
     '    side_popup("运算", &["模式", "颜色", "Hz/格", "其他"], tab);', 1),
    ("scope_ui.rs",
     'pub const WINDOWS: [&str; 6] = ["Rectangular", "Blackman", "Hanning", "Hamming", "Triangular", "Flat-top"];',
     'pub const WINDOWS: [&str; 6] = ["矩形", "布莱克曼", "汉宁", "汉明", "三角", "平顶"];', 1),
    ("scope_ui.rs",
     '            fill_text(r, pc, C_POP_BG, sf::SC_F16, r, "Window", C_BAR, 8, 0);',
     '            fill_text(r, pc, C_POP_BG, sf::TEXT22, r, "窗函数", C_BAR, 8, 0);', 1),
    ("scope_ui.rs",
     '            fill_text(r, pc, C_POP_BG, sf::SC_F16, r, "FFT Unit", C_BAR, 8, 0);',
     '            fill_text(r, pc, C_POP_BG, sf::TEXT22, r, "FFT 单位", C_BAR, 8, 0);', 1),

    # ------------------------------------------------------------- timebase / hint
    ("scope_ui.rs",
     '    let t = Ink::new(sf::SC_F16, TB_HEAD, "Time/div", 8, 0);',
     '    let t = Ink::new(sf::TEXT22, TB_HEAD, "时间/格", 8, 0);', 1),
    ("scope_ui.rs",
     '    rbox_text(rect(190, 150, 100, 20), rect(0, 0, 480, 320), 8, C_PURPLE, C_FILL, sf::SC_F16, "Sampling", C_WHITE);',
     '    rbox_text(rect(190, 150, 100, 24), rect(0, 0, 480, 320), 8, C_PURPLE, C_FILL, sf::TEXT22, "采样中", C_WHITE);', 1),

    # ------------------------------------------------------------------ settings
    ("ui.rs",
     '    ("Power", &[S_SHUTDOWN, S_RAILS, S_REMEMBER]),',
     '    ("电源", &[S_SHUTDOWN, S_RAILS, S_REMEMBER]),', 1),

    # -------------------------------------------------------------------- decode
    ("ui_decode.rs",
     'const DL_TEXTS: [&str; 6] = ["协议：", "模式：", "Bit rate:", "极性：", "阈值：", ""];',
     'const DL_TEXTS: [&str; 6] = ["协议：", "模式：", "位速率：", "极性：", "阈值：", ""];', 1),
    ("ui_decode.rs",
     '        let k = Ink::new(sf::SC_F16, *r, t, 1, 0);',
     '        let k = Ink::new(sf::TEXT22, *r, t, 1, 0);', 1),
    ("ui_decode.rs",
     '    let modes: &[&str] = if LOG { &["Band", "Log"] } else { &["Band"] };',
     '    let modes: &[&str] = if LOG { &["带状", "日志"] } else { &["带状"] };', 1),

    # -------------------------------------------------------------- trigger source
    ("scope.rs",
     'pub const TSRC_NAMES: [&str; 2] = ["CH1", "GEN"];',
     'pub const TSRC_NAMES: [&str; 2] = ["通道", "信源"];', 1),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="upstream firmware/src after apply_dict.py")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    by_file = {}
    for f, old, new, n in PATCHES:
        by_file.setdefault(f, []).append((old, new, n))

    total = 0
    for f in sorted(by_file):
        path = os.path.join(a.src, f)
        if not os.path.isfile(path):
            sys.exit("scope_zh.py: missing %s" % path)
        text = io.open(path, encoding="utf-8").read()
        edits = 0
        for old, new, n in by_file[f]:
            if new in text:
                continue
            hits = text.count(old)
            if hits != n:
                sys.exit("%s: expected %d hit(s), found %d for: %s"
                         % (f, n, hits, old.split("\n")[0][:90]))
            text = text.replace(old, new)
            edits += 1
        if edits and not a.dry_run:
            io.open(path, "w", encoding="utf-8", newline="\n").write(text)
        total += edits
        print("%-16s %d edit(s)%s" % (f, edits, " [dry run]" if a.dry_run else ""))

    print("%d edit(s) total%s" % (total, " [dry run]" if a.dry_run else ""))


if __name__ == "__main__":
    main()
