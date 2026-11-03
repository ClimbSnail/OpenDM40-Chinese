import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) power.rs：加一个「上一次原始读数」的全局，并把冻结逻辑暂时旁路
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()
if "RAW_MV" not in t:
    t = t.replace("const TS_SLOPE: f32 = 0.0043;",
                  "const TS_SLOPE: f32 = 0.0043;\n\n"
                  "/// TEMP 调试：最近一次未经处理的电池读数（毫伏）。\n"
                  "pub static RAW_MV: core::sync::atomic::AtomicU32 =\n"
                  "    core::sync::atomic::AtomicU32::new(0);")
    t = t.replace("        let v = convert(15) as f32 * 3.0 / 4096.0 * 2.0;",
                  "        let v = convert(15) as f32 * 3.0 / 4096.0 * 2.0;\n"
                  "        RAW_MV.store((v * 1000.0) as u32, core::sync::atomic::Ordering::Relaxed);")
    io.open(P, "w", encoding="utf-8", newline="\n").write(t)
    print("power.rs: 加了 RAW_MV")
else:
    print("power.rs 已有 RAW_MV")

# 2) ui.rs：把电压画在开机时长的位置
Q = S + r"\ui.rs"
u = io.open(Q, encoding="utf-8").read()
old = "    sf::label(sf::F21, rect(205, 5, 112, 24), hms(&mut t, st.uptime_s), STATUS_FG, BAR, 1, -1);"
new = """    // TEMP 调试：显示电池原始读数（毫伏）
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
if old in u:
    u = u.replace(old, new)
    io.open(Q, "w", encoding="utf-8", newline="\n").write(u)
    print("ui.rs: 改成显示毫伏")
else:
    print("ui.rs 锚点没找到")
