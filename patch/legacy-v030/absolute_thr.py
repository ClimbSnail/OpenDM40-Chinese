import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) power.rs：改成按电压绝对值 + 迟滞判定
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

old = """        let v = convert(15) as f32 * 3.0 / 4096.0 * 2.0;
        /// USB in or out shows as a step in the reading (measured 2026-11-03:
        /// 4 bars on battery, 5 bars the moment the cable goes in).
        const JUMP: f32 = 0.12;
        if self.vbat < 1.0 {
            self.vbat = v; // first reading after boot
        } else if v - self.vbat > JUMP {
            self.chg = true; // USB just went in: keep the pre-charge level
        } else if self.vbat - v > JUMP {
            self.chg = false; // USB pulled: this step is the real level
            self.vbat = v;
        } else if !self.chg {
            self.vbat = v; // on battery: track normally
        }"""
new = """        let v = convert(15) as f32 * 3.0 / 4096.0 * 2.0;
        RAW_MV.store((v * 1000.0) as u32, core::sync::atomic::Ordering::Relaxed);
        /// Charging holds the cell at the TP4056's CV point: measured 2026-11-03,
        /// 4.199..4.204 V on the cable against 4.054 V on battery, so the level
        /// alone tells the two apart. A jump detector was tried first and lost
        /// to CV ripple (the state kept flipping and stuck in "charging").
        const HI: f32 = 4.13;
        const LO: f32 = 4.09;
        if v > HI {
            self.chg = true;
        } else if v < LO {
            self.chg = false;
        }
        // While charging the reading is the charger's 4.2 V, not the cell's
        // level: keep the last real one (and take the first reading after a
        // boot whatever it is, there is nothing to keep).
        if !self.chg || self.vbat < 1.0 {
            self.vbat = v;
        }"""
if old not in t:
    raise SystemExit("poll 锚点没找到")
t = t.replace(old, new)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 改为 4.13/4.09 绝对值判定")

# 2) ui.rs：撤掉毫伏显示，恢复开机时长
Q = S + r"\ui.rs"
u = io.open(Q, encoding="utf-8").read()
old_ui = """    // TEMP 调试：显示电池原始读数（毫伏）
    let mv = crate::power::RAW_MV.load(core::sync::atomic::Ordering::Relaxed);
    let mut dt = [b'0'; 4];
    {
        let mut v = mv;
        for i in (0..4).rev() {
            dt[i] = b'0' + (v % 10) as u8;
            v /= 10;
        }
    }
    let ds = core::str::from_utf8(&dt).unwrap_or("0000");
    sf::label(sf::F21, rect(205, 5, 112, 24), ds, 0x07FF, BAR, 1, -1);"""
new_ui = "    sf::label(sf::F21, rect(205, 5, 112, 24), hms(&mut t, st.uptime_s), STATUS_FG, BAR, 1, -1);"
if old_ui in u:
    u = u.replace(old_ui, new_ui)
    io.open(Q, "w", encoding="utf-8", newline="\n").write(u)
    print("ui.rs: 恢复开机时长")
else:
    print("ui.rs 锚点没找到（可能已恢复）")
