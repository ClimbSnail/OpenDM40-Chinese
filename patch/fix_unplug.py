import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

# 1) 加 prev 字段
t = t.replace("""    /// Resting level the reading is compared against (mV->V).
    rest: f32,""",
              """    /// Resting level the reading is compared against (mV->V).
    rest: f32,
    /// Previous reading, for the drop that a pulled cable makes.
    prev: f32,""")
t = t.replace("chg: false, rest: 0.0 }", "chg: false, rest: 0.0, prev: 0.0 }")

# 2) 拔线改成「比上一秒掉了一截」
old = """        } else if v - self.rest < OFF {
            self.chg = false;
        }"""
new = """        } else if v < self.prev - OFF {
            // Cable pulled: the reading falls by the IR drop at once. Comparing
            // against the pre-charge baseline instead was wrong: after a part
            // charge the resting level rises above it, so "v - rest" stayed
            // over the OFF margin and the icon kept blinking (seen 2026-11-04).
            self.chg = false;
            self.rest = v;
        }
        self.prev = v;"""
if old not in t:
    raise SystemExit("拔线判定锚点没找到")
t = t.replace(old, new)

# OFF 阈值改成电压差（0.05 V）
t = t.replace("        const OFF: f32 = 0.05;",
              "        /// 拔线时读数掉下来的幅度门限（实测约 0.19 V）。\n"
              "        const OFF: f32 = 0.05;")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power.rs: 拔线改成看电压跌落（比上一秒低 50 mV）")
