#!/usr/bin/env python3
"""Move 暗屏方式 beside 暗屏时间, and give both timeouts more choices.

Page 1 (power / display) becomes:
    暗屏时间 暗屏方式 关机时间 背光亮度 蜂鸣音量 蓝牙 开机屏 电源方式 更多
Page 2 (DMM / scope) becomes:
    采样率 平滑 显示行 温度单位 示波器滑动 示波器按键 点击档位 示波器拖动 更多

"示波器拖动" is a scope setting, so moving it to page 2 keeps page 1 at nine
rows -- a tenth would not fit (30 px pitch from y=44 runs off a 320 px screen).

Timeouts (ascending, 永不 last):
    暗屏 15秒 30秒 1分 2分 5分 10分 30分 永不
    关机  1分  5分 10分 30分 1小时 2小时 永不

The indices were 2-bit fields (`p[0] & 3`); both masks widen to 4 bits so eight
values fit. After this build the stored value re-reads as a new index, so the
timeouts may land on a different entry once -- set them from the UI.

    python mkpatch24.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
UI = os.path.join(SRC, "ui.rs")
APP = os.path.join(SRC, "app.rs")

ui = io.open(UI, encoding="utf-8").read()
app = io.open(APP, encoding="utf-8").read()


def sub(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    return text.replace(old, new)


# ---- 1. the two row tables ------------------------------------------
ui = sub(ui,
         '"暗屏时间", "关机时间", "背光亮度", "蜂鸣音量", "蓝牙", "开机屏", "电源方式",\n    "示波器拖动", "更多",',
         '"暗屏时间", "暗屏方式", "关机时间", "背光亮度", "蜂鸣音量", "蓝牙", "开机屏",\n    "电源方式", "更多",',
         "SETTINGS rows")

ui = sub(ui, '    "暗屏方式",\n', '    "示波器拖动",\n', "SETTINGS2 rows")

# ---- 2. the time tables ---------------------------------------------
app = sub(app,
          'const DIM_MS: [u64; 4] = [300_000, 600_000, 1_800_000, 0];\n'
          'const OFF_MS: [u64; 4] = [600_000, 1_800_000, 3_600_000, 0];\n'
          'const DIM_TXT: [&str; 4] = ["5\u5206", "10\u5206", "30\u5206", "\u6c38\u4e0d"];\n'
          'const OFF_TXT: [&str; 4] = ["10\u5206", "30\u5206", "1\u5c0f\u65f6", "\u6c38\u4e0d"];',
          '/// \u6697\u5c4f\u8d85\u65f6, \u7531\u77ed\u5230\u957f, 0 = \u6c38\u4e0d (\u6700\u540e\u4e00\u9879).\n'
          'const DIM_MS: [u64; 8] = [15_000, 30_000, 60_000, 120_000, 300_000, 600_000, 1_800_000, 0];\n'
          '/// \u5173\u673a\u8d85\u65f6, \u7531\u77ed\u5230\u957f, 0 = \u6c38\u4e0d.\n'
          'const OFF_MS: [u64; 7] = [60_000, 300_000, 600_000, 1_800_000, 3_600_000, 7_200_000, 0];\n'
          'const DIM_TXT: [&str; 8] = ["15\u79d2", "30\u79d2", "1\u5206", "2\u5206", "5\u5206", "10\u5206", "30\u5206", "\u6c38\u4e0d"];\n'
          'const OFF_TXT: [&str; 7] = ["1\u5206", "5\u5206", "10\u5206", "30\u5206", "1\u5c0f\u65f6", "2\u5c0f\u65f6", "\u6c38\u4e0d"];',
          "time tables")

# ---- 3. the 2-bit masks become 4-bit --------------------------------
app = sub(app, 'self.dim_idx = (p[0] & 3) as usize;',
          'self.dim_idx = (p[0] & 0xF) as usize;', "dim mask")
app = sub(app, 'self.off_idx = (p[0] >> 4 & 3) as usize;',
          'self.off_idx = (p[0] >> 4 & 0xF) as usize;', "off mask")

# ---- 4. page 1 values ------------------------------------------------
old_vals = (
    '                let grab = gesture::grab_ms();\n'
    '                let mut gb = [0u8; 16];\n'
    '                let grab_txt = if grab == 0 {\n'
    '                    scope_page::DRAG_NAMES[self.sp.drag_mode.min(1) as usize]\n'
    '                } else {\n'
    '                    let mut t = [0u8; 16];\n'
    '                    let s = crate::dmm::format(&mut t, grab as f32, 0);\n'
    '                    gb[..5].copy_from_slice(b"Hold ");\n'
    '                    gb[5..5 + s.len()].copy_from_slice(s.as_bytes());\n'
    '                    gb[5 + s.len()..8 + s.len()].copy_from_slice(b" ms");\n'
    '                    core::str::from_utf8(&gb[..8 + s.len()]).unwrap_or("Hold")\n'
    '                };\n'
    '                let vals: [&str; 9] = [\n'
    '                    DIM_TXT[self.dim_idx],\n'
    '                    OFF_TXT[self.off_idx],\n'
    '                    core::str::from_utf8(&b0[..n0]).unwrap_or(""),\n'
    '                    core::str::from_utf8(&b1[..n1]).unwrap_or(""),\n'
    '                    if self.bt_on { "\u5f00" } else { "\u5173" },\n'
    '                    ui::view_name(START[self.start_page]),\n'
    '                    if self.rails_both { "\u4e24\u8005\u5e38\u5f00" } else { "\u81ea\u52a8 (\u6309\u89c6\u56fe)" },\n'
    '                    grab_txt,\n'
    '                    "", // More row: opens page 2, no inline value\n'
    '                ];'
)
new_vals = (
    '                let vals: [&str; 9] = [\n'
    '                    DIM_TXT[self.dim_idx],\n'
    '                    if self.dim_glow { "\u5fae\u5149" } else { "\u5168\u9ed1" },\n'
    '                    OFF_TXT[self.off_idx],\n'
    '                    core::str::from_utf8(&b0[..n0]).unwrap_or(""),\n'
    '                    core::str::from_utf8(&b1[..n1]).unwrap_or(""),\n'
    '                    if self.bt_on { "\u5f00" } else { "\u5173" },\n'
    '                    ui::view_name(START[self.start_page]),\n'
    '                    if self.rails_both { "\u4e24\u8005\u5e38\u5f00" } else { "\u81ea\u52a8 (\u6309\u89c6\u56fe)" },\n'
    '                    "", // More row: opens page 2, no inline value\n'
    '                ];'
)
app = sub(app, old_vals, new_vals, "page-1 values")

# ---- 5. page 2 values: the drag text takes the freed slot -----------
old_p2 = (
    '                    crate::scope_ui::TAP_NAMES[self.sp.tap_mode.min(2) as usize],\n'
    '                    if self.dim_glow { "\u5fae\u5149" } else { "\u5168\u9ed1" },\n'
)
new_p2 = (
    '                    crate::scope_ui::TAP_NAMES[self.sp.tap_mode.min(2) as usize],\n'
    '                    if gesture::grab_ms() == 0 {\n'
    '                        scope_page::DRAG_NAMES[self.sp.drag_mode.min(1) as usize]\n'
    '                    } else {\n'
    '                        "\u6309\u4f4f"\n'
    '                    },\n'
)
app = sub(app, old_p2, new_p2, "page-2 values")

# ---- 6. page 1 taps: renumbered -------------------------------------
old_taps = (
    '                    Some(0) => self.dim_idx = (self.dim_idx + 1) % 4,\n'
    '                    Some(1) => self.off_idx = (self.off_idx + 1) % 4,\n'
    '                    // -/+ steppers (ui-review #12): 10 % steps, clamped.\n'
    '                    Some(2) => {\n'
    '                        let d = ui::settings_step(x) as i16 * 10;\n'
    '                        self.backlight = (self.backlight as i16 + d).clamp(10, 100) as u8;\n'
    '                        backlight(self.backlight);\n'
    '                    }\n'
    '                    Some(3) => {\n'
    '                        let d = ui::settings_step(x) as i16 * 10;\n'
    '                        self.volume = (self.volume as i16 + d).clamp(0, 100) as u8;\n'
    '                    }\n'
    '                    Some(4) => self.bt_on = !self.bt_on,\n'
    '                    Some(5) => self.start_page = (self.start_page + 1) % 4,\n'
    '                    Some(6) => {\n'
    '                        let b = !self.rails_both;\n'
    '                        self.set_rails_both(b, clk);\n'
    '                    }\n'
)
new_taps = (
    '                    Some(0) => self.dim_idx = (self.dim_idx + 1) % DIM_TXT.len(),\n'
    '                    Some(1) => self.dim_glow = !self.dim_glow,\n'
    '                    Some(2) => self.off_idx = (self.off_idx + 1) % OFF_TXT.len(),\n'
    '                    // -/+ steppers (ui-review #12): 10 % steps, clamped.\n'
    '                    Some(3) => {\n'
    '                        let d = ui::settings_step(x) as i16 * 10;\n'
    '                        self.backlight = (self.backlight as i16 + d).clamp(10, 100) as u8;\n'
    '                        backlight(self.backlight);\n'
    '                    }\n'
    '                    Some(4) => {\n'
    '                        let d = ui::settings_step(x) as i16 * 10;\n'
    '                        self.volume = (self.volume as i16 + d).clamp(0, 100) as u8;\n'
    '                    }\n'
    '                    Some(5) => self.bt_on = !self.bt_on,\n'
    '                    Some(6) => self.start_page = (self.start_page + 1) % 4,\n'
    '                    Some(7) => {\n'
    '                        let b = !self.rails_both;\n'
    '                        self.set_rails_both(b, clk);\n'
    '                    }\n'
)
app = sub(app, old_taps, new_taps, "page-1 taps")

# the old drag arm on page 1 goes away entirely
old_drag = (
    '                    Some(7) => {\n'
    '                        // Scope drag: Stock (per-event) -> Axis lock -> Hold\n'
    '                        // 300 ms (hold-to-grab, doc \u64026.2) -> Stock.\n'
    '                        if gesture::grab_ms() != 0 {\n'
    '                            gesture::set_grab_ms(0);\n'
    '                            self.sp.drag_mode = scope_page::DRAG_STOCK;\n'
    '                        } else if self.sp.drag_mode == scope_page::DRAG_STOCK {\n'
    '                            self.sp.drag_mode = scope_page::DRAG_AXIS;\n'
    '                        } else {\n'
    '                            self.sp.drag_mode = scope_page::DRAG_STOCK;\n'
    '                            gesture::set_grab_ms(gesture::GRAB_DEFAULT_MS);\n'
    '                        }\n'
    '                    }\n'
)
if old_drag in app:
    app = app.replace(old_drag, '')
else:
    sys.stderr.write("note: page-1 drag arm already gone or differs\n")

# ---- 7. page 2 taps: the drag cycle takes the freed slot ------------
app = sub(app,
          '                    Some(7) => self.dim_glow = !self.dim_glow,\n',
          '                    Some(7) => {\n'
          '                        // Scope drag: Stock (per-event) -> Axis lock -> Hold\n'
          '                        // 300 ms (hold-to-grab) -> Stock.\n'
          '                        if gesture::grab_ms() != 0 {\n'
          '                            gesture::set_grab_ms(0);\n'
          '                            self.sp.drag_mode = scope_page::DRAG_STOCK;\n'
          '                        } else if self.sp.drag_mode == scope_page::DRAG_STOCK {\n'
          '                            self.sp.drag_mode = scope_page::DRAG_AXIS;\n'
          '                        } else {\n'
          '                            self.sp.drag_mode = scope_page::DRAG_STOCK;\n'
          '                            gesture::set_grab_ms(gesture::GRAB_DEFAULT_MS);\n'
          '                        }\n'
          '                    }\n',
          "page-2 taps")

io.open(UI, "w", encoding="utf-8", newline="\n").write(ui)
io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("done: rows reordered, 8/7 timeout choices, 4-bit indices\n")
