import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"


def sub(path, old, new, tag):
    p = S + "\\" + path
    t = io.open(p, encoding="utf-8").read()
    if t.count(old) != 1:
        raise SystemExit("%s: 命中 %d 次" % (tag, t.count(old)))
    io.open(p, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
    print("改了:", tag)


# ---- 1. Status 加一个闪烁相位 ----
sub("ui.rs", """    /// Index of the shown view in View::CYCLE (page dots), 255 = none.
    pub page: u8,
}""", """    /// Index of the shown view in View::CYCLE (page dots), 255 = none.
    pub page: u8,
    /// Charging blink phase (true = top cell drawn): the app flips it once
    /// per status refresh, so the topmost cell blinks while charging.
    pub blink: bool,
}""", "Status.blink")

# ---- 2. 充电时的颜色 + 闪烁 ----
sub("ui.rs", """fn battery_glyph(b: &mut [u8; 4], bars: u8) -> &str {
    char::from_u32(0x22 + bars.min(5) as u32).unwrap_or('"').encode_utf8(b)
}""", """fn battery_glyph(b: &mut [u8; 4], bars: u8) -> &str {
    char::from_u32(0x22 + bars.min(5) as u32).unwrap_or('"').encode_utf8(b)
}

/// Battery while charging: green (the stock scope's C_GREEN), and the
/// topmost filled cell blinks off/on with `Status::blink`.
const CHG_GREEN: Color = 0x07E0;

/// The level to draw: while charging with the blink phase off, one cell less
/// (the topmost filled one), which reads as that cell blinking.
fn battery_bars(st: &Status) -> u8 {
    if st.charging && !st.blink { st.bars.saturating_sub(1) } else { st.bars }
}""", "CHG_GREEN + battery_bars")

sub("ui.rs", """    let bc = if st.charging { 0x04A9 } else { STATUS_FG };""",
    """    let bc = if st.charging { CHG_GREEN } else { STATUS_FG };""", "DMM 电池绿色")

sub("ui.rs", """    sf::label(sf::BATTERY, rect(435, 9, 40, 16), battery_glyph(&mut b, st.bars), bc, BAR, 8, 0);""",
    """    sf::label(sf::BATTERY, rect(435, 9, 40, 16), battery_glyph(&mut b, battery_bars(st)), bc, BAR, 8, 0);""",
    "DMM 用闪烁档位")

# ---- 3. app 里给相位 ----
sub("app.rs", """            page: View::CYCLE.iter().position(|&v| v == self.view).map_or(255, |i| i as u8),
        }""", """            page: View::CYCLE.iter().position(|&v| v == self.view).map_or(255, |i| i as u8),
            blink: self.strip_alt,
        }""", "app 传 blink")

io.open(S + r"\ui.rs", "a", encoding="utf-8", newline="\n").write("")
print("完成")
