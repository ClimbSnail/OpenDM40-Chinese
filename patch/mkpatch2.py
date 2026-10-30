#!/usr/bin/env python3
"""Apply the Chinese UI patch to a pristine firmware/src/ui.rs.

Two groups:
  * the settings pages (page titles + the three label arrays)
  * the main menu tiles, the gallery row, the combined-view row and
    `view_name` (which is also the "Start page" setting's value and the
    title bar of most pages)

Every replacement is checked to occur exactly once, so a source change
upstream makes this fail loudly instead of patching the wrong thing.

    python mkpatch2.py PRISTINE_UI_RS OUT_UI_RS
"""

import io
import sys

SRC, DST = sys.argv[1], sys.argv[2]
src = io.open(SRC, encoding="utf-8").read()
orig_len = len(src.encode())

REPS = [
    # ---------------- settings: page 1 / 2 / 3 labels -------------------
    (
        'pub const SETTINGS: [&str; 9] = [\n'
        '    "Dim screen", "Shutdown", "Backlight", "Key/alert volume", "Bluetooth", "Start page", "Analog power",\n'
        '    "Scope drag", "More",\n'
        '];',
        'pub const SETTINGS: [&str; 9] = [\n'
        '    "\u6697\u5c4f\u65f6\u95f4", "\u5173\u673a\u65f6\u95f4", "\u80cc\u5149\u4eae\u5ea6", "\u8702\u9e23\u97f3\u91cf", "\u84dd\u7259", "\u5f00\u673a\u5c4f", "\u7535\u6e90\u65b9\u5f0f",\n'
        '    "\u793a\u6ce2\u5668\u62d6\u52a8", "\u66f4\u591a",\n'
        '];',
    ),
    (
        'pub const SETTINGS2: [&str; 9] = ["DMM rate", "Smoothing", "DMM row", "Temp unit", "Scope swipe", "Scope press", "Scope tap step", "Help", "More"];',
        'pub const SETTINGS2: [&str; 9] = [\n'
        '    "\u91c7\u6837\u7387", "\u5e73\u6ed1", "\u663e\u793a\u884c", "\u6e29\u5ea6\u5355\u4f4d", "\u793a\u6ce2\u5668\u6ed1\u52a8", "\u793a\u6ce2\u5668\u6309\u952e", "\u70b9\u51fb\u6863\u4f4d", "\u5e2e\u52a9",\n'
        '    "\u66f4\u591a",\n'
        '];',
    ),
    (
        'pub const SETTINGS3: [&str; 8] = ["Jack alerts", "Danger alarm", "USB disk", "Burden voltage", "Device", "Touch test", "Accuracy", "Negative ohm"];',
        'pub const SETTINGS3: [&str; 8] = [\n'
        '    "\u544a\u8b66\u5f00\u5173", "\u5371\u9669\u8b66\u62a5", "U\u76d8", "\u8d1f\u62c5\u7535\u538b", "\u8bbe\u5907", "\u89e6\u6478\u6d4b\u8bd5", "\u51c6\u786e\u5ea6",\n'
        '    "\u8d1f\u7535\u963b",\n'
        '];',
    ),
    ('list_page("Settings", &SETTINGS, &v[..vals.len().min(9)]);',
     'list_page("\u8bbe\u7f6e", &SETTINGS, &v[..vals.len().min(9)]);'),
    ('list_page("Settings 2/3", &SETTINGS2, vals);',
     'list_page("\u8bbe\u7f6e 2/3", &SETTINGS2, vals);'),
    ('list_page("Settings 3/3", &SETTINGS3, vals);',
     'list_page("\u8bbe\u7f6e 3/3", &SETTINGS3, vals);'),

    # ---------------- main menu tiles ----------------------------------
    ('"Multimeter", 0x20', '"\u4e07\u7528\u8868", 0x20'),
    ('"Oscilloscope", 0x21', '"\u793a\u6ce2\u5668", 0x21'),
    ('"Signal", 0x22', '"\u4fe1\u53f7\u6e90", 0x22'),
    ('"Settings", 0x23', '"\u8bbe\u7f6e", 0x23'),

    # ---------------- gallery row + combined-view row ------------------
    ('"Gallery: screenshots and logs"', '"\u56fe\u5e93 \u622a\u56fe\u8bb0\u5f55"'),
    ('let pre = b"Combined view: ";', 'let pre = "\u7ec4\u5408\u89c6\u56fe ";'),
    ('t[..pre.len()].copy_from_slice(pre);', 't[..pre.len()].copy_from_slice(pre.as_bytes());'),

    # ---------------- view_name (page titles + Start page value) -------
    ('View::Dmm => "Multimeter",', 'View::Dmm => "\u4e07\u7528\u8868",'),
    ('View::Scope => "Oscilloscope",', 'View::Scope => "\u793a\u6ce2\u5668",'),
    ('View::Gen => "Signal",', 'View::Gen => "\u4fe1\u53f7\u6e90",'),
    ('View::DmmScope => "DMM + Scope",', 'View::DmmScope => "\u4e07\u7528\u8868+\u793a\u6ce2\u5668",'),
    ('View::Menu => "Main menu",', 'View::Menu => "\u4e3b\u83dc\u5355",'),
    ('View::Settings => "Settings",', 'View::Settings => "\u8bbe\u7f6e",'),
    ('View::Range => "Range",', 'View::Range => "\u91cf\u7a0b",'),
    ('View::Keypad => "Keypad",', 'View::Keypad => "\u952e\u76d8",'),
    ('View::Device => "Device",', 'View::Device => "\u8bbe\u5907",'),
    ('View::Limits => "Hold & Limits",', 'View::Limits => "\u4fdd\u6301\u9650\u503c",'),
    ('View::Record => "Record",', 'View::Record => "\u8bb0\u5f55",'),
    ('View::Gallery => "Gallery",', 'View::Gallery => "\u56fe\u5e93",'),
    ('View::Help => "Help",', 'View::Help => "\u5e2e\u52a9",'),
    ('View::Inrush => "Inrush",', 'View::Inrush => "\u6d8c\u6d41",'),
    ('View::TouchTest => "Touch test",', 'View::TouchTest => "\u89e6\u6478\u6d4b\u8bd5",'),
]

for old, new in REPS:
    n = src.count(old)
    if n != 1:
        sys.exit("NOT FOUND / AMBIGUOUS (%d occurrences): %r" % (n, old[:70]))
    src = src.replace(old, new)

io.open(DST, "w", encoding="utf-8", newline="\n").write(src)
sys.stderr.write("applied %d replacements, ui.rs %d -> %d bytes\n"
                 % (len(REPS), orig_len, len(src.encode())))
