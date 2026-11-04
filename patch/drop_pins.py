import io
import re

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

# 已经不用充电芯片的状态脚了：把上拉配置和 GPIOB 常量删掉
old_cfg = """            // PB10 / PB11 = the charger's open-drain status pins. The stock
            // firmware reads them with pull-ups (hw/README.md: "in, pull-up");
            // without one a released pin floats and reads 0, which looks like
            // "charging" all the time (seen 2026-11-03: the icon kept blinking
            // after the cable was pulled).
            modify32(GPIOB + 0x00, (3 << 20) | (3 << 22), 0); // PB10, PB11 input
            modify32(GPIOB + 0x0C, (3 << 20) | (3 << 22), (1 << 20) | (1 << 22)); // pull-up
"""
if old_cfg in t:
    t = t.replace(old_cfg, "")
    print("删掉 PB10/PB11 上拉配置")

if "GPIOB" in t and len(re.findall(r"GPIOB", t)) == 1:
    t = re.sub(r"const GPIOB: u32 = 0x4002_0400;\n", "", t)
    print("删掉 GPIOB 常量")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("剩余 GPIOB 引用:", len(re.findall(r"GPIOB", t)))
