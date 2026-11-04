import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

# 1) 去掉 prev 字段（RAM 不够 4 字节），充电时复用 rest 记录充电电压
t = t.replace("""    /// Previous reading, for the drop that a pulled cable makes.
    prev: f32,
""", "")
t = t.replace("chg: false, rest: 0.0, prev: 0.0 }", "chg: false, rest: 0.0 }")

# 2) 拔线判定改用 rest（充电期间它记录的是充电电压）
old = """        } else if v < self.prev - OFF {
            // Cable pulled: the reading falls by the IR drop at once. Comparing
            // against the pre-charge baseline instead was wrong: after a part
            // charge the resting level rises above it, so "v - rest" stayed
            // over the OFF margin and the icon kept blinking (seen 2026-11-04).
            self.chg = false;
            self.rest = v;
        }
        self.prev = v;"""
new = """        } else if v < self.rest - OFF {
            // Cable pulled: the reading falls by the IR drop at once. `rest`
            // holds the last *charging* reading here (the pre-charge baseline
            // was wrong: after a part charge the resting level rose above it,
            // so the icon kept blinking - seen 2026-11-04).
            self.chg = false;
            self.rest = v;
        } else {
            self.rest = v; // charging: follow the reading so a pull shows
        }"""
if old not in t:
    raise SystemExit("拔线判定锚点没找到")
t = t.replace(old, new)

# 3) 清掉过时的两段注释（说的是绝对电压那套）
t = t.replace("""        // Charging holds the cell at the TP4056's CV point: measured 2026-11-03,
        // 4.199..4.204 V on the cable against 4.054 V on battery, so the level
        // alone tells the two apart. A step detector was tried first and lost
        // to CV ripple (the state kept flipping and stuck in "charging").
""", "")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 去掉 prev，改用 rest 兼作充电电压记录")
