#!/usr/bin/env python3
"""Add "暗屏方式" (screen-off mode): fully dark or a 5 % glow.

The meter already dimmed to 5 % after the idle timeout. This adds a choice and
makes **fully dark** the default, which is what was asked for:

    全黑    backlight 0   (new default)
    微光    backlight 5   (the old behaviour)

Storage: `p[0]` is full up to bit 14 (bit 13 retired, 14 the SCPI IDN flag), so
bit 15 takes the flag and no record version has to move.

The row goes on settings page 2, which has space for nine rows again after the
help row was removed.

    python mkpatch23.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]

UI = os.path.join(SRC, "ui.rs")
APP = os.path.join(SRC, "app.rs")

ui = io.open(UI, encoding="utf-8").read()
app = io.open(APP, encoding="utf-8").read()

# ---- 1. the settings row --------------------------------------------
old = 'pub const SETTINGS2: [&str; 8] = ['
if ui.count(old) != 1:
    sys.exit("SETTINGS2 head not found")
ui = ui.replace(old, 'pub const SETTINGS2: [&str; 9] = [')

# insert 暗屏方式 just before 更多
old = '"点击档位",\n    "更多",'
if ui.count(old) != 1:
    sys.exit("SETTINGS2 tail not found (%d)" % ui.count(old))
ui = ui.replace(old, '"点击档位",\n    "暗屏方式",\n    "更多",')

# ---- 2. the field, its default and the dim action --------------------
old = '    dimmed: bool,'
if app.count(old) != 1:
    sys.exit("dimmed field not found")
app = app.replace(old, '        dimmed: bool,\n'
                       '    /// 暗屏方式: false = 全黑 (backlight 0), true = 微光 (5 %);\n'
                       '        /// p[0] bit 15 (0 = the default 全黑).\n'
                       '    dim_glow: bool,')

old = '            dimmed: false,'
if app.count(old) != 1:
    sys.exit("dimmed init not found")
app = app.replace(old, '            dimmed: false,\n            dim_glow: false,')

old = '''            self.dimmed = true;
            backlight(0);'''
if app.count(old) != 1:
    sys.exit("dim action not found")
app = app.replace(old, '''            self.dimmed = true;
            backlight(if self.dim_glow { 5 } else { 0 });''')

# ---- 3. persistence --------------------------------------------------
old = '            | (crate::scpi::idn_emul() as u32 & 1) << 14;'
if app.count(old) != 1:
    sys.exit("persist p[0] tail not found")
app = app.replace(old, '            | (crate::scpi::idn_emul() as u32 & 1) << 14\n'
                       '            | (self.dim_glow as u32) << 15;')

old = '        crate::scpi::set_idn_emul((p[0] >> 14 & 1) as u8);'
if app.count(old) != 1:
    sys.exit("restore p[0] not found")
app = app.replace(old, '        crate::scpi::set_idn_emul((p[0] >> 14 & 1) as u8);\n'
                       '        self.dim_glow = p[0] >> 15 & 1 != 0;')

# ---- 4. the page-2 value and its tap --------------------------------
old = '                    crate::scope_ui::TAP_NAMES[self.sp.tap_mode.min(2) as usize],\n'
if app.count(old) != 1:
    sys.exit("page-2 tap value not found")
app = app.replace(old, old + '                    if self.dim_glow { "微光" } else { "全黑" },\n')

old = '                    Some(7) => self.set_page = 2,'
if app.count(old) != 1:
    sys.exit("More arm not found")
app = app.replace(old, '                    Some(7) => self.dim_glow = !self.dim_glow,\n'
                       '                    Some(8) => self.set_page = 2,')

# ---- 5. the test timeout back to 5 minutes --------------------------
old = 'const DIM_MS: [u64; 4] = [20_000, 600_000, 1_800_000, 0];'
if app.count(old) != 1:
    sys.exit("test DIM_MS not found")
app = app.replace(old, 'const DIM_MS: [u64; 4] = [300_000, 600_000, 1_800_000, 0];')

io.open(UI, "w", encoding="utf-8", newline="\n").write(ui)
io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("done: row + field + persist bit 15 + timeout restored\n")
