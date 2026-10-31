import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub("fill_text(h, screen, C_POP_TAB, sf::SC_F16, h, title, C_YELLOW, 8, 0);",
    "fill_text(h, screen, C_POP_TAB, sf::TEXT22, h, title, C_YELLOW, 8, 0);", "title")
sub("let ink = Ink::new(sf::SC_F16, r, t, 8, 1);",
    "let ink = Ink::new(sf::TEXT22, r, t, 8, 1);", "tabs")
sub('side_popup("CHA", &["Coupling", "Probe", "Color"], tab);',
    'side_popup("CHA", &["耦合", "探头", "颜色"], tab);', "cha")
sub('side_popup("MATH", &["Mode", "Color", "Hz/Div", "Other"], tab);',
    'side_popup("MATH", &["模式", "颜色", "Hz/格", "其他"], tab);', "math")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("scope popups localized")
