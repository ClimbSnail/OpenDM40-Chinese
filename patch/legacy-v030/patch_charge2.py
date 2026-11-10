import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

P = S + r"\ui.rs"
t = io.open(P, encoding="utf-8").read()
n1 = t.count("let bc = if st.charging { 0x04A9 } else { STATUS_FG };")
t = t.replace("let bc = if st.charging { 0x04A9 } else { STATUS_FG };",
              "let bc = if st.charging { CHG_GREEN } else { STATUS_FG };")
n2 = t.count("battery_glyph(&mut b, st.bars)")
t = t.replace("battery_glyph(&mut b, st.bars)", "battery_glyph(&mut b, battery_bars(st))")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: 颜色 %d 处，档位 %d 处" % (n1, n2))

A = S + r"\app.rs"
a = io.open(A, encoding="utf-8").read()
old = """            page: View::CYCLE.iter().position(|&v| v == self.view).map_or(255, |i| i as u8),
        }"""
new = """            page: View::CYCLE.iter().position(|&v| v == self.view).map_or(255, |i| i as u8),
            blink: self.strip_alt,
        }"""
assert a.count(old) == 1
io.open(A, "w", encoding="utf-8", newline="\n").write(a.replace(old, new))
print("app.rs: blink 已传入")
