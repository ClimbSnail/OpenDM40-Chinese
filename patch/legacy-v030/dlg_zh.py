import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\dialog.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub('centred((b.0, b.1, b.2, 40), "Power off?", FG, TITLE_BG);',
    'centred((b.0, b.1, b.2, 40), "关机？", FG, TITLE_BG);', "title")
sub('centred((b.0, b.1 + 40, b.2, 60), "Cancels in 3 s", FG, BODY_BG);',
    'centred((b.0, b.1 + 40, b.2, 60), "3 秒后取消", FG, BODY_BG);', "body")
sub('centred((b.0, b.1, b.2, 40), "Reset energy?", FG, TITLE_BG);',
    'centred((b.0, b.1, b.2, 40), "清零电能？", FG, TITLE_BG);', "reset title")
sub('centred((b.0, b.1 + 40, b.2, 60), "Wh, VAh and the time", FG, BODY_BG);',
    'centred((b.0, b.1 + 40, b.2, 60), "电能与时间", FG, BODY_BG);', "reset body")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("power-off / reset dialogs localized")
