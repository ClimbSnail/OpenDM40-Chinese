import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# the two buttons of the measure tab (60 px wide: two hanzi fit)
sub('rbox_text(rect(281, 176, 60, 30), pc, 8, C_ORANGE, C_POP_BG, sf::SC_F16, "Clear", C_WHITE);',
    'rbox_text(rect(281, 176, 60, 30), pc, 8, C_ORANGE, C_POP_BG, sf::TEXT22, "清除", C_WHITE);',
    "clear")
sub('rbox_text(rect(348, 176, 60, 30), pc, 8, C_PURPLE, C_POP_BG, sf::SC_F16, "Default", C_WHITE);',
    'rbox_text(rect(348, 176, 60, 30), pc, 8, C_PURPLE, C_POP_BG, sf::TEXT22, "默认", C_WHITE);',
    "default")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("measure tab buttons localized")
