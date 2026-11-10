import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\ui.rs"
t = io.open(P, encoding="utf-8").read()

old = """/// Battery while charging: a soft green (0, 190, 110), pulsed between two
/// brightnesses by `Status::blink` instead of dropping a cell - the pure
/// 0x07E0 of the scope reads as a highlighter on the dark bar, and a
/// disappearing cell looked like a glitch.
const CHG_GREEN: Color = 0x05ED;
const CHG_GREEN_DIM: Color = 0x02C6;

/// The level to draw: always the real one (the blink is a brightness pulse).
fn battery_bars(st: &Status) -> u8 {
    st.bars
}"""
new = """/// Battery while charging: a soft green (0, 190, 110) - the pure 0x07E0 of
/// the scope reads as a highlighter on the dark bar. `Status::blink` drops
/// the topmost filled cell, so one cell blinks off/on at 1 Hz.
const CHG_GREEN: Color = 0x05ED;

/// The level to draw: while charging with the blink phase off, one cell less
/// (the topmost filled one), which reads as that cell blinking.
fn battery_bars(st: &Status) -> u8 {
    if st.charging && !st.blink { st.bars.saturating_sub(1) } else { st.bars }
}"""
if old not in t:
    raise SystemExit("锚点 1 没找到")
t = t.replace(old, new)

old2 = """    let bc = if st.charging {
        if st.blink { CHG_GREEN } else { CHG_GREEN_DIM }
    } else {
        STATUS_FG
    };"""
new2 = """    let bc = if st.charging { CHG_GREEN } else { STATUS_FG };"""
if old2 not in t:
    raise SystemExit("锚点 2 没找到")
t = t.replace(old2, new2)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: 恢复单格闪烁，颜色保留柔和绿")
