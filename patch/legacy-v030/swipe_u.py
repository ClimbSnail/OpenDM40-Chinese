import io

# 1) SCPI: accept "U" for a synthetic swipe up
P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scpi.rs"
t = io.open(P, encoding="utf-8").read()
OLD = """                            Some(&b'D') => {
                                let n = a.split(|&b| b == b',').nth(1).and_then(parse_num).unwrap_or(1.0);
                                Dbg::Input(4, (n as u16).clamp(1, 5), 0)
                            }"""
NEW = """                            Some(&b'D') => {
                                let n = a.split(|&b| b == b',').nth(1).and_then(parse_num).unwrap_or(1.0);
                                Dbg::Input(4, (n as u16).clamp(1, 5), 0)
                            }
                            // U: synthetic one-finger swipe up (scrolls the
                            // settings list down); tests and scripted checks.
                            Some(&b'U') => Dbg::Input(5, 0, 0),"""
if t.count(OLD) != 1:
    raise SystemExit("scpi anchor %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)

# 2) main: dispatch it
P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\main.rs"
t = io.open(P, encoding="utf-8").read()
OLD = """                            4 => gestures.synth_swipe_down(x as u8, now), // DBG:SWIPE D,n"""
NEW = """                            4 => gestures.synth_swipe_down(x as u8, now), // DBG:SWIPE D,n
                            5 => Some(gesture::Gesture::SwipeUp), // DBG:SWIPE U"""
if t.count(OLD) != 1:
    raise SystemExit("main anchor %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("DBG:SWIPE U added")
