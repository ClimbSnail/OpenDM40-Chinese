import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) 注册模块
P = S + r"\main.rs"
t = io.open(P, encoding="utf-8").read()
if "mod splash_anim;" not in t:
    old = "mod ad2pll;\n"
    assert t.count(old) == 1
    t = t.replace(old, old + "mod splash_anim;\n")
    io.open(P, "w", encoding="utf-8", newline="\n").write(t)
    print("main.rs: mod splash_anim 已注册")

# 2) 在 show() 里调用（不在 draw() 里：draw 被主机渲染工具复用）
Q = S + r"\native\splash.rs"
import os
Q = os.path.join(S, "splash.rs")
s = io.open(Q, encoding="utf-8").read()
old = """pub fn show() {
    draw();
    crate::persist::init();"""
new = """pub fn show() {
    draw();
    // 一段约 200 ms 的扫描动画，之后再让进度条跟着启动阶段走。
    crate::splash_anim::play();
    crate::persist::init();"""
if old not in s:
    raise SystemExit("show() 锚点没找到")
s = s.replace(old, new)
io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
print("splash.rs: show() 已插入动画调用")
