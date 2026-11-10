import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()

old = """            modify32(GPIOC, 3 << 10, 3 << 10); // PC5 analog"""
new = """            // PB10 / PB11 = the charger's open-drain status pins. The stock
            // firmware reads them with pull-ups (hw/README.md: "in, pull-up");
            // without one a released pin floats and reads 0, which looks like
            // "charging" all the time (seen 2026-11-03: the icon kept blinking
            // after the cable was pulled).
            modify32(GPIOB + 0x00, (3 << 20) | (3 << 22), 0); // PB10, PB11 input
            modify32(GPIOB + 0x0C, (3 << 20) | (3 << 22), (1 << 20) | (1 << 22)); // pull-up
            modify32(GPIOC, 3 << 10, 3 << 10); // PC5 analog"""
if old not in t:
    raise SystemExit("锚点没找到")
io.open(P, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
print("power.rs: PB10/PB11 加了上拉")
