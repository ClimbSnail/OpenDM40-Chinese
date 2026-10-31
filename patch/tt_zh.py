import io

# ---- touch test page: everything drawn with TEXT22 ----------------------
P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui_touchtest.rs"
t = io.open(P, encoding="utf-8").read()

PAIRS = [
    ('("Keep holding to exit", C_DOWN)', '("继续按住即退出", C_DOWN)'),
    ('("Exit: power key, hold 2 s", M_ACCENT)', '("退出：长按电源键 2 秒", M_ACCENT)'),
    ('rect(LINE_X + 12, LEGEND_Y, 44, 20), "raw"', 'rect(LINE_X + 12, LEGEND_Y, 44, 20), "原始"'),
    ('rect(LINE_X + 74, LEGEND_Y, 100, 20), "corrected"', 'rect(LINE_X + 74, LEGEND_Y, 100, 20), "校正后"'),
    ('rect(LINE_X + 203, LEGEND_Y, 60, 20), "down"', 'rect(LINE_X + 203, LEGEND_Y, 60, 20), "按下"'),
    ('button(CALIB, "Calibrate");', 'button(CALIB, "校准");'),
    ('button(CLEAR, "Clear");', 'button(CLEAR, "清除");'),
    # the calibration wizard
    ('w_line(0, "Touch calibration", M_ACCENT);', 'w_line(0, "触摸校准", M_ACCENT);'),
    ('w_line(1, "Tap the yellow cross", STATUS_FG);', 'w_line(1, "点击黄色十字", STATUS_FG);'),
    ('button(BTN[0], "Cancel");', 'button(BTN[0], "取消");'),
    ('button(BTN[1], "Reset");', 'button(BTN[1], "重置");'),
    ('t.s("Point ").u(i as u32 + 1).s(" of ").u(TARGETS.len() as u32).s(", tap ").u(tap as u32 + 1).s(" of ").u(taps as u32);',
     't.s("第 ").u(i as u32 + 1).s(" / ").u(TARGETS.len() as u32).s(" 点，第 ").u(tap as u32 + 1).s(" / ").u(taps as u32).s(" 次");'),
    ('t.s("Fit error: mean ").d(mean).s(", max ").d(max).s(" px");',
     't.s("拟合误差 均值 ").d(mean).s(" 最大 ").d(max).s(" px");'),
    ('t.s("Before: mean ").d(before).s(" px");', 't.s("校准前 均值 ").d(before).s(" px");'),
    ('None => cal_msg("Good fit: Save applies it", false),', 'None => cal_msg("拟合良好，保存后生效", false),'),
    ('button(BTN[0], if bad.is_none() { "Save" } else { "Try again" });',
     'button(BTN[0], if bad.is_none() { "保存" } else { "重试" });'),
    # the F14 formula lines have no "Cal" word any more
    ('t[0].s("Cal: none (stock)");', 't[0].s("\\u539f\\u5382\\u6821\\u51c6");'),
    ('t[0].s("Cal ");', 't[0].s("");'),
    ('t[1].s("Cal ");', 't[1].s("");'),
]
for old, new in PAIRS:
    if t.count(old) != 1:
        raise SystemExit("%r -> %d" % (old[:40], t.count(old)))
    t = t.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

# ---- wiring dialog: the two TEXT22 buttons ----------------------------
P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui_power.rs"
t = io.open(P, encoding="utf-8").read()
OLD = '''    for (r, l, c) in [(DLG_CANCEL, "Cancel", BTN), (DLG_OK, "OK", SEL)] {'''
NEW = '''    for (r, l, c) in [(DLG_CANCEL, "取消", BTN), (DLG_OK, "确定", SEL)] {'''
if t.count(OLD) != 1:
    raise SystemExit("wiring buttons %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("touch test + wiring buttons localized")
