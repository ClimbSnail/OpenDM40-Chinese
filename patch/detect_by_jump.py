import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

# 1) 结构体加一个充电标志
old = """pub struct Power {
    next: u64,
    pub vbat: f32,
    pub bars: u8,
    /// MCU die temperature, C (NaN until the first read).
    pub mcu_t: f32,
}"""
new = """pub struct Power {
    next: u64,
    pub vbat: f32,
    pub bars: u8,
    /// MCU die temperature, C (NaN until the first read).
    pub mcu_t: f32,
    /// Charging, from the step in the battery reading when USB goes in/out
    /// (see `poll`): PB10/PB11 are open-drain charger pins that read the same
    /// whether the cable is in or out on this board, so they are not used.
    chg: bool,
}"""
if old not in t:
    raise SystemExit("结构体锚点没找到")
t = t.replace(old, new)

t = t.replace("Power { next: 0, vbat: 4.2, bars: 5, mcu_t: f32::NAN }",
              "Power { next: 0, vbat: 0.0, bars: 5, mcu_t: f32::NAN, chg: false }")

# 2) charging() 读标志
old_chg = """    pub fn charging(&self) -> bool {
        let b = unsafe { r32(GPIOB + 0x10) };
        b & (1 << 11) == 0
    }"""
new_chg = """    pub fn charging(&self) -> bool {
        self.chg
    }"""
if old_chg not in t:
    raise SystemExit("charging 锚点没找到")
t = t.replace(old_chg, new_chg)

# 3) poll 用跳变判断
old_poll = """        // 充电时 USB 的供电通路把读数抬高（实测插线 2 s 就跳到满格），
        // 所以这一路只在没充电时采信，充电期间保留充电前的电量。
        if !self.charging() {
            self.vbat = convert(15) as f32 * 3.0 / 4096.0 * 2.0;
        } else {
            let _ = convert(15);
        }"""
new_poll = """        let v = convert(15) as f32 * 3.0 / 4096.0 * 2.0;
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
if old_poll not in t:
    raise SystemExit("poll 锚点没找到")
t = t.replace(old_poll, new_poll)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 改用电压跳变判断充电")
