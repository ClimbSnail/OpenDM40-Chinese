import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) 用 paint + clip 画：外框白、内部格子绿（照 scope_ui::battery 的做法）
P = S + r"\ui.rs"
t = io.open(P, encoding="utf-8").read()

old = """    sf::label(sf::BATTERY, rect(435, 9, 40, 16), battery_glyph(&mut b, battery_bars(st)), bc, BAR, 8, 0);
}"""
new = """    battery_icon(st);
}

/// Battery with the outline in `STATUS_FG` and only the cells in the charging
/// green: the level glyph (0x22 + n) carries its own outline, so it is clipped
/// to the interior (the stock scope battery, scope_ui::battery, does the same).
fn battery_icon(st: &Status) {
    let r = rect(435, 9, 40, 16);
    let o = sf::Ink::icon(sf::BATTERY, r, 0x22, 0);
    let lv = battery_bars(st);
    let l = if lv > 0 {
        sf::Ink::icon(sf::BATTERY, r, 0x22 + lv.min(5) as u32, 0)
    } else {
        sf::Ink::none()
    };
    let clip = rect(437, 11, 33, 12);
    let lc = if st.charging { CHG_GREEN } else { STATUS_FG };
    sf::paint(r, &[(0, BAR)], |x, y| {
        if clip.has(x, y) {
            if let Some(g) = l.at(x, y) {
                return (lc, g as u16);
            }
        }
        match o.at(x, y) {
            Some(g) => (STATUS_FG, g as u16),
            None => (BAR, 0),
        }
    });
}"""
if old not in t:
    raise SystemExit("status_right 尾部没找到")
t = t.replace(old, new)

# 2) 旧的 bc 变量不再需要（保留不会错，但会警告）；battery_glyph 变成未使用
t = t.replace("    let bc = if st.charging { CHG_GREEN } else { STATUS_FG };\n", "")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: 电池改成 paint+clip（外框白、格子绿）")
