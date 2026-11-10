import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) 结构体加 rest（静置基准）
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

t = t.replace("""    /// Charging, from the step in the battery reading when USB goes in/out
    /// (see `poll`): PB10/PB11 are open-drain charger pins that read the same
    /// whether the cable is in or out on this board, so they are not used.
    chg: bool,""",
              """    /// Charging, from how far the reading sits above the resting level.
    /// The charger's status pins (PB10/PB11) do not change with the cable on
    /// this board and are not used; the IR drop in the cell is reliable
    /// instead (measured 2026-11-03: 4155 mV charging against 3966 mV a moment
    /// after the cable is pulled, i.e. ~190 mV).
    chg: bool,
    /// Resting level the reading is compared against (mV->V).
    rest: f32,""")

t = t.replace("Power { next: 0, vbat: 0.0, bars: 5, mcu_t: f32::NAN, chg: false }",
              "Power { next: 0, vbat: 0.0, bars: 5, mcu_t: f32::NAN, chg: false, rest: 0.0 }")

old = """        // TP4056 /CHRG on PB10, active low (full charge releases it and pulls
        // /STDBY low, which was the state measured first: PB10=1, PB11=0).
        let idr = unsafe { r32(GPIOB + 0x10) };
        self.chg = idr & (1 << 10) == 0;"""
new = """        // Charging = the reading sits above the resting level by the cell's
        // IR drop (~190 mV measured); released, it falls back at once.
        const ON: f32 = 0.08;
        const OFF: f32 = 0.05;
        if self.rest < 1.0 {
            self.rest = v; // first reading after boot
        } else if !self.chg {
            // On battery: the resting level follows the discharge.
            self.rest += (v - self.rest) * 0.02;
            if v - self.rest > ON {
                self.chg = true;
            }
        } else if v - self.rest < OFF {
            self.chg = false;
        }"""
if old not in t:
    raise SystemExit("poll 判定锚点没找到")
t = t.replace(old, new)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 改用 IR 压降判定（ON 80 mV / OFF 50 mV）")

# 2) ui.rs：撤掉毫伏显示
Q = S + r"\ui.rs"
u = io.open(Q, encoding="utf-8").read()
i = u.find("    // TEMP 调试：电压（mV）与 GPIOB 输入寄存器")
if i > 0:
    j = u.find("\n", u.find("sf::label(sf::F21, rect(205, 5, 112, 24), ds, 0x07FF, BAR, 1, -1);", i))
    u = u[:i] + "    sf::label(sf::F21, rect(205, 5, 112, 24), hms(&mut t, st.uptime_s), STATUS_FG, BAR, 1, -1);" + u[j:]
    io.open(Q, "w", encoding="utf-8", newline="\n").write(u)
    print("ui.rs: 恢复开机时长")
else:
    print("ui.rs: 没找到调试块")
