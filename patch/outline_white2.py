import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\ui.rs"
t = io.open(P, encoding="utf-8").read()

# 信号源状态栏那条也改成电池图标（外框白、格子绿），并给它自己的 y
old = """    sf::label(sf::BATTERY, rect(435, 10, 40, 16), battery_glyph(&mut b, battery_bars(st)), bc, G_BAR, 8, 0);"""
new = """    battery_icon_at(st, 10, G_BAR);"""
if old not in t:
    raise SystemExit("信号源电池行没找到")
t = t.replace(old, new)

# battery_icon 增加 var 版本
old2 = """fn battery_icon(st: &Status) {
    let r = rect(435, 9, 40, 16);"""
new2 = """fn battery_icon(st: &Status) {
    battery_icon_at(st, 9, BAR);
}

/// Same, at `y` (the DMM bar draws at 9, the generator bar at 10) over `bg`.
fn battery_icon_at(st: &Status, y: i16, bg: Color) {
    let r = rect(435, y, 40, 16);"""
if old2 not in t:
    raise SystemExit("battery_icon 头没找到")
t = t.replace(old2, new2)

# 函数体里的 BAR 换成 bg，clip 的 y 跟着 y 走
body_old = """    let clip = rect(437, 11, 33, 12);
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
body_new = """    let clip = rect(437, y + 2, 33, 12);
    let lc = if st.charging { CHG_GREEN } else { STATUS_FG };
    sf::paint(r, &[(0, bg)], |px, py| {
        if clip.has(px, py) {
            if let Some(g) = l.at(px, py) {
                return (lc, g as u16);
            }
        }
        match o.at(px, py) {
            Some(g) => (STATUS_FG, g as u16),
            None => (bg, 0),
        }
    });
}"""
if body_old not in t:
    raise SystemExit("battery_icon 体没找到")
t = t.replace(body_old, body_new)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: 两条状态栏都改用电池图标函数")
