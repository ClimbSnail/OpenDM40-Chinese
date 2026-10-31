#!/usr/bin/env python3
"""Add "蜂鸣音调": pick the buzzer drive frequency, i.e. hunt its resonance.

The volume knob is already maxed: `buzz_k(100)` is 0.495, i.e. 49.5 % duty,
which is the most AC a square wave can carry -- the code comment calls it "the
loudest the stock drives". Nothing above that gets louder.

What is left is the drive frequency. TIM14 runs from 40 MHz and the period is
`BUZZER_ARR` (11,200 -> 3.571 kHz). A piezo or magnetic buzzer only reaches its
rated output near resonance, so a frequency that misses it can be several dB
quieter. The vendor fixed one value; on a different batch of buzzers another
may be louder.

Rows on settings page 3 (it had room for one more):
    蜂鸣音调  2.7k / 3.0k / 3.6k / 4.0k / 4.5k      default 3.6k (unchanged)

Stored in p[0] bits 16..19 (0 = default). The chosen period goes into a static
so `buzzer()` and `buzzer_tone()` -- free functions without access to `App` --
see it.

    python mkpatch25.py FIRMWARE_SRC_DIR
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


# ---- 1. the row -----------------------------------------------------
# SETTINGS3 has eight rows; either form ("[&str; 8]" one line or wrapped) is
# handled by inserting before the closing bracket of the array.
m = ui.find("pub const SETTINGS3: [&str; 8] = [")
if m < 0:
    sys.exit("SETTINGS3 not found")
end = ui.find("];", m)
ui = ui[:end] + '    "蜂鸣音调",\n' + ui[end:]
ui = ui.replace("pub const SETTINGS3: [&str; 8] = [", "pub const SETTINGS3: [&str; 9] = [", 1)

# ---- 2. the frequency table and the shared period -------------------
app = sub(app,
          'const BUZZER_ARR: u32 = 11200;',
          'const BUZZER_ARR: u32 = 11200;\n'
          '/// 蜂鸣音调: TIM14 周期, 40 MHz / ARR = 频率.\n'
          'const BUZZ_ARR: [u32; 5] = [14815, 13333, 11200, 10000, 8889];\n'
          'const BUZZ_TXT: [&str; 5] = ["2.7k", "3.0k", "3.6k", "4.0k", "4.5k"];\n'
          '/// The period actually in use (the setting writes it).\n'
          'static BUZZ_PERIOD: core::sync::atomic::AtomicU32 =\n'
          '    core::sync::atomic::AtomicU32::new(11200);\n'
          'fn buzz_period() -> u32 {\n'
          '    BUZZ_PERIOD.load(core::sync::atomic::Ordering::Relaxed)\n'
          '}',
          "BUZZER_ARR")

# ---- 3. use it in the two drivers -----------------------------------
app = sub(app,
          '    let duty = if on { (BUZZER_ARR as f32 * buzz_k(vol)) as u32 } else { 0 };',
          '    let duty = if on { (buzz_period() as f32 * buzz_k(vol)) as u32 } else { 0 };',
          "buzzer duty")

app = sub(app,
          '    let arr = if tone == 2 { BUZZER_ARR_LO } else { BUZZER_ARR };',
          '    let arr = if tone == 2 { BUZZER_ARR_LO } else { buzz_period() };',
          "buzzer_tone arr")

# ---- 4. the field, its default, persistence ------------------------
app = sub(app, '    dim_glow: bool,',
          '    dim_glow: bool,\n'
          '    /// 蜂鸣音调 (BUZZ_ARR index); p[0] bits 16..19.\n'
          '    buzz_idx: usize,',
          "field")

app = sub(app, '            dim_glow: false,',
          '            dim_glow: false,\n            buzz_idx: 2,',
          "init")

app = sub(app,
          '            | (self.dim_glow as u32) << 15;',
          '            | (self.dim_glow as u32) << 15\n'
          '            | (self.buzz_idx as u32) << 16;',
          "persist")

app = sub(app,
          '        self.dim_glow = p[0] >> 15 & 1 != 0;',
          '        self.dim_glow = p[0] >> 15 & 1 != 0;\n'
          '        self.buzz_idx = (p[0] >> 16 & 0xF) as usize;\n'
          '        if self.buzz_idx >= BUZZ_ARR.len() {\n'
          '            self.buzz_idx = 2;\n'
          '        }\n'
          '        BUZZ_PERIOD.store(BUZZ_ARR[self.buzz_idx], core::sync::atomic::Ordering::Relaxed);',
          "restore")

# ---- 5. page 3 value and tap ---------------------------------------
app = sub(app,
          '                    if self.dmm.ohm_neg { "开" } else { "关 (原厂)" },',
          '                    if self.dmm.ohm_neg { "开" } else { "关 (原厂)" },\n'
          '                    BUZZ_TXT[self.buzz_idx.min(4)],',
          "page-3 value")

app = sub(app,
          '                    Some(7) => {\n'
          '                        // Negative ohm: from the next reading on.\n'
          '                        self.dmm.ohm_neg = !self.dmm.ohm_neg;\n'
          '                    }\n'
          '                    Some(_) | None => return,',
          '                    Some(7) => {\n'
          '                        // Negative ohm: from the next reading on.\n'
          '                        self.dmm.ohm_neg = !self.dmm.ohm_neg;\n'
          '                    }\n'
          '                    Some(8) => {\n'
          '                        // 蜂鸣音调: next drive frequency; a short beep\n'
          '                        // previews it so it can be picked by ear.\n'
          '                        self.buzz_idx = (self.buzz_idx + 1) % BUZZ_ARR.len();\n'
          '                        BUZZ_PERIOD.store(BUZZ_ARR[self.buzz_idx],\n'
          '                                          core::sync::atomic::Ordering::Relaxed);\n'
          '                        self.beep(clk.now_ms(), 60);\n'
          '                    }\n'
          '                    Some(_) | None => return,',
          "page-3 tap")

io.open(UI, "w", encoding="utf-8", newline="\n").write(ui)
io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("done: 蜂鸣音调 row + BUZZ_ARR + shared period\n")
