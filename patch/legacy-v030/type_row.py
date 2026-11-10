import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# 窄脉冲 is 66 px wide: widen the row and its cells
sub("pub const TT_LIST: Rect = rect(24, 136, 180, 24);",
    "pub const TT_LIST: Rect = rect(24, 136, 200, 24);", "const")
sub("option_list(TT_LIST, pc, &crate::trigsoft::TYPE_NAMES, 60, v.ttype.min(2) as usize);",
    "option_list(TT_LIST, pc, &crate::trigsoft::TYPE_NAMES, 66, v.ttype.min(2) as usize);", "draw")
sub("} else if let Some(i) = option_hit(TT_LIST, 3, 60, x, y) {",
    "} else if let Some(i) = option_hit(TT_LIST, 3, 66, x, y) {", "hit")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("type row widened to 200 / 66")
