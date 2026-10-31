import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# ---- display tab: labels in 22 px (no colon, keeps the row rhythm) -----
sub('''            for (r, t) in [(rect(24, 61, 189, 20), "Roll:"), (rect(24, 105, 189, 20), "Persist:"), (rect(214, 61, 189, 20), "Brightness:"), (rect(214, 105, 189, 20), "Grid intensity:")] {
                fill_text(r, pc, C_POP_BG, sf::SC_F16, r, t, C_FILL, 1, 0);
            }
            option_list(rect(24, 81, 88, 24), pc, &["On", "Off"], 44, if v.roll { 0 } else { 1 });
            option_list(rect(24, 125, 176, 24), pc, &["OFF", "MIN", "1S", "INF"], 44, v.persist as usize);''',
    '''            for (r, t) in [(rect(24, 58, 189, 22), "滚动"), (rect(24, 102, 189, 22), "余辉"), (rect(214, 58, 189, 22), "亮度"), (rect(214, 102, 189, 22), "网格")] {
                fill_text(r, pc, C_POP_BG, sf::TEXT22, r, t, C_FILL, 1, 0);
            }
            option_list(rect(24, 81, 88, 24), pc, &["开", "关"], 44, if v.roll { 0 } else { 1 });
            option_list(rect(24, 125, 176, 24), pc, &["关", "最小", "1s", "∞"], 44, v.persist as usize);''',
    "display")

# ---- settings tab: the two buttons ------------------------------------
sub('rbox_text(rect(24, 78, 80, 30), pc, 8, C_BAR, C_POP_BG, sf::SC_F16, "PriScr", C_WHITE);',
    'rbox_text(rect(24, 78, 80, 30), pc, 8, C_BAR, C_POP_BG, sf::TEXT22, "截屏", C_WHITE);',
    "priscr")
sub('rbox_text(rect(114, 78, 80, 30), pc, 8, C_BAR, C_POP_BG, sf::SC_F16, "Save CSV", C_WHITE);',
    'rbox_text(rect(114, 78, 80, 30), pc, 8, C_BAR, C_POP_BG, sf::TEXT22, "存CSV", C_WHITE);',
    "savecsv")

# ---- trigger tab: give the labels a little air ------------------------
sub('fill_text(rect(24, 59, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 59, 189, 22), "边沿：", C_FILL, 1, 0);',
    'fill_text(rect(24, 57, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 57, 189, 22), "边沿", C_FILL, 1, 0);',
    "edge")
sub('fill_text(rect(214, 59, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(214, 59, 189, 22), "模式：", C_FILL, 1, 0);',
    'fill_text(rect(214, 57, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(214, 57, 189, 22), "模式", C_FILL, 1, 0);',
    "mode")
sub('fill_text(TT_LABEL, pc, C_POP_BG, sf::TEXT22, TT_LABEL, "类型：", C_FILL, 1, 0);',
    'fill_text(rect(24, 114, 180, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 114, 180, 22), "类型", C_FILL, 1, 0);',
    "type")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("scope display/settings tabs localized")
