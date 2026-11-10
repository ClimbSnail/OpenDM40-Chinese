import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\ui.rs"
t = io.open(P, encoding="utf-8").read()

old = """/// The level to draw: while charging with the blink phase off, one cell less
/// (the topmost filled one), which reads as that cell blinking.
fn battery_bars(st: &Status) -> u8 {
    if st.charging && !st.blink { st.bars.saturating_sub(1) } else { st.bars }
}"""
new = """/// The level to draw. While charging the cell being filled blinks: with room
/// left the next cell appears and disappears (4 -> 5 -> 4), and when the pack
/// reads full the top cell itself blinks (5 -> 4 -> 5).
fn battery_bars(st: &Status) -> u8 {
    if !st.charging {
        st.bars
    } else if st.bars >= 5 {
        if st.blink { 5 } else { 4 }
    } else if st.blink {
        st.bars + 1
    } else {
        st.bars
    }
}"""
if old not in t:
    raise SystemExit("锚点没找到")
io.open(P, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
print("ui.rs: 改成闪下一格")
