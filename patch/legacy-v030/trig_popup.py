import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# the option lists in the trigger popup are ASCII-only at 16 px
sub("fill_text_on(ir, clip, bg, C_BAR, sf::SC_F16, ir, t, fg, 8, 0);",
    "fill_text_on(ir, clip, bg, C_BAR, sf::TEXT22, ir, t, fg, 8, 0);", "font")
sub('&["Rising", "Falling"]', '&["上升", "下降"]', "slope")
sub('&["Auto", "Normal", "Single"]', '&["自动", "常规", "单次"]', "mode")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("trigger popup localized")
