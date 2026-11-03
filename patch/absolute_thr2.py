import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

old = """        /// USB in or out shows as a step in the reading (measured 2026-11-03:
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
new = """        // Charging holds the cell at the TP4056's CV point: measured 2026-11-03,
        // 4.199..4.204 V on the cable against 4.054 V on battery, so the level
        // alone tells the two apart. A step detector was tried first and lost
        // to CV ripple (the state kept flipping and stuck in "charging").
        const HI: f32 = 4.13;
        const LO: f32 = 4.09;
        if v > HI {
            self.chg = true;
        } else if v < LO {
            self.chg = false;
        }
        // While charging the reading is the charger's 4.2 V, not the cell's
        // level: keep the last real one (the first reading after a boot is
        // taken whatever it is, there is nothing to keep).
        if !self.chg || self.vbat < 1.0 {
            self.vbat = v;
        }"""
if old not in t:
    raise SystemExit("poll 锚点没找到")
io.open(P, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
print("power.rs: 改为 4.13/4.09 绝对值判定")
