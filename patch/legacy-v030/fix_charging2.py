import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

# 1) 判定：PB11 低 = 正在充电（实测：插线未满电时 PB10=1, PB11=0）
old = """    pub fn charging(&self) -> bool {
        let b = unsafe { r32(GPIOB + 0x10) };
        b & (1 << 10) == 0 && b & (1 << 11) != 0
    }"""
new = """    pub fn charging(&self) -> bool {
        let b = unsafe { r32(GPIOB + 0x10) };
        b & (1 << 11) == 0
    }"""
if old not in t:
    raise SystemExit("charging 锚点没找到")
t = t.replace(old, new)

# 注释同步
t = t.replace("""    /// TP4056 status pins, active low: PB10 = /CHRG (low while charging),
    /// PB11 = /STDBY (low when the charge is complete). Both float high
    /// (pull-ups) with no charger, so "PB10 low, PB11 high" is the only
    /// combination that means charging. 2026-11-03: this was previously
    /// "both high", which is the *idle* state and never showed charging.""",
              """    /// TP4056 /CHRG on PB11, active low. Measured on the meter (2026-11-03,
    /// unit on USB, battery not full): GPIOB IDR = 0x8400, i.e. PB10 high and
    /// PB11 low, which is the charging state; with the battery full the same
    /// unit read PB10 high / PB11 low only while unplugged. The old test
    /// ("both high") is the *no charger* state and never showed charging.""")

# 2) 充电时不再采信电池电压（USB 一插读数就被抬高，2 秒显示满电）
old_poll = """        self.vbat = convert(15) as f32 * 3.0 / 4096.0 * 2.0;"""
new_poll = """        // 充电时 USB 的供电通路把读数抬高（实测插线 2 s 就跳到满格），
        // 所以这一路只在没充电时采信，充电期间保留充电前的电量。
        if !self.charging() {
            self.vbat = convert(15) as f32 * 3.0 / 4096.0 * 2.0;
        } else {
            let _ = convert(15);
        }"""
if old_poll not in t:
    raise SystemExit("vbat 锚点没找到")
t = t.replace(old_poll, new_poll)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 充电判定改为 PB11 低；充电期间冻结点电量")
