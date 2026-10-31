import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# labels back inside the clipping area (pc starts at y=61)
sub('(rect(24, 58, 189, 22), "滚动"), (rect(24, 102, 189, 22), "余辉"), (rect(214, 58, 189, 22), "亮度"), (rect(214, 102, 189, 22), "网格")',
    '(rect(24, 61, 189, 20), "滚动"), (rect(24, 105, 189, 20), "余辉"), (rect(214, 61, 189, 20), "亮度"), (rect(214, 105, 189, 20), "网格")',
    "display labels")

sub('fill_text(rect(24, 57, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 57, 189, 22), "边沿", C_FILL, 1, 0);',
    'fill_text(rect(24, 61, 189, 20), pc, C_POP_BG, sf::TEXT22, rect(24, 61, 189, 20), "边沿", C_FILL, 1, 0);',
    "edge")
sub('fill_text(rect(214, 57, 189, 22), pc, C_POP_BG, sf::TEXT22, rect(214, 57, 189, 22), "模式", C_FILL, 1, 0);',
    'fill_text(rect(214, 61, 189, 20), pc, C_POP_BG, sf::TEXT22, rect(214, 61, 189, 20), "模式", C_FILL, 1, 0);',
    "mode")
sub('fill_text(rect(24, 114, 180, 22), pc, C_POP_BG, sf::TEXT22, rect(24, 114, 180, 22), "类型", C_FILL, 1, 0);',
    'fill_text(TT_LABEL, pc, C_POP_BG, sf::TEXT22, TT_LABEL, "类型", C_FILL, 1, 0);',
    "type")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("labels back at y=61/105")
