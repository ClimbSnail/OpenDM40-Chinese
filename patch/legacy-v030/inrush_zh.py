import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app_inrush_live.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub('Phase::Arming => ("Arming ...", ui::inr::C_ARMED),',
    'Phase::Arming => ("准备中…", ui::inr::C_ARMED),', "arming")
sub('Phase::Armed => (cat(b, &["Armed: ", ui::inr::amps(&mut t, self.inrush_live_a()), " A now"]), ui::inr::C_ARMED),',
    'Phase::Armed => (cat(b, &["就绪 ", ui::inr::amps(&mut t, self.inrush_live_a()), " A"]), ui::inr::C_ARMED),', "armed")
sub('Phase::Post => ("Triggered: recording 2 s ...", ui::inr::C_TRIG),',
    'Phase::Post => ("已触发：记录 2 秒…", ui::inr::C_TRIG),', "post")
sub('("Cancel", 0xF800, true)', '("取消", 0xF800, true)', "cancel")
sub('("Saving ...", ui::BTN, false)', '("保存中…", ui::BTN, false)', "saving")
sub('("Arm", ui::SEL, true)', '("就绪", ui::SEL, true)', "arm")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

Q = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui_power.rs"
s = io.open(Q, encoding="utf-8").read()
OLD = 't.push("Aborted");'
NEW = 't.push("已中止");'
if s.count(OLD) != 1:
    raise SystemExit("aborted: %d" % s.count(OLD))
s = s.replace(OLD, NEW)
io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
print("inrush page + aborted localized")
