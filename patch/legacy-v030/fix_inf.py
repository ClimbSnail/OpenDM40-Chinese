import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\scope_ui.rs"
t = io.open(P, encoding="utf-8").read()
OLD = '&["\u5173", "\u6700\u5c0f", "1s", "\u221e"]'
NEW = '&["\u5173", "\u6700\u5c0f", "1s", "\u65e0\u9650"]'
if t.count(OLD) != 1:
    raise SystemExit("count %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("inf -> wuxian")
