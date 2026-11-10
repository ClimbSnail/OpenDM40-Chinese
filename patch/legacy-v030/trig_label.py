import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub('fill_text(rect(24, 61, 189, 20), pc, C_POP_BG, sf::SC_F16, rect(24, 61, 189, 20), "Edge:", C_FILL, 1, 0);',
    'fill_text(rect(24, 59, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 59, 189, 22), "边沿：", C_FILL, 1, 0);',
    "edge")
sub('fill_text(rect(214, 61, 189, 20), pc, C_POP_BG, sf::SC_F16, rect(214, 61, 189, 20), "Mode:", C_FILL, 1, 0);',
    'fill_text(rect(214, 59, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(214, 59, 189, 22), "模式：", C_FILL, 1, 0);',
    "mode")
sub('fill_text(TT_LABEL, pc, C_POP_BG, sf::SC_F16, TT_LABEL, "Type:", C_FILL, 1, 0);',
    'fill_text(TT_LABEL, pc, C_POP_BG, sf::TEXT22, TT_LABEL, "类型：", C_FILL, 1, 0);',
    "type")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

Q = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\trigsoft.rs"
s = io.open(Q, encoding="utf-8").read()
OLD = 'pub const TYPE_NAMES: [&str; 3] = ["Edge", "Pulse", "Runt"];'
NEW = 'pub const TYPE_NAMES: [&str; 3] = ["边沿", "脉冲", "窄脉冲"];'
if s.count(OLD) != 1:
    raise SystemExit("type_names %d" % s.count(OLD))
s = s.replace(OLD, NEW)
io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
print("trigger labels + types localized")
