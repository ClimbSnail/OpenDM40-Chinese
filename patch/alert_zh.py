import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\sentinel.rs"
t = io.open(P, encoding="utf-8").read()

PAIRS = [
    ('Alert::Overload => "Overload: 10 A shunt selected"', 'Alert::Overload => "过载：已切到 10 A 分流"'),
    ('Alert::AJack => "Current in A jack: check leads"', 'Alert::AJack => "A 插孔有电流，请检查表笔"'),
    ('Alert::AProt => "A jack current: 10 A shunt on"', 'Alert::AProt => "A 插孔有电流，已开 10 A 分流"'),
    ('Alert::VJack => "Voltage on V jack, no current"', 'Alert::VJack => "V 插孔有电压，无电流"'),
    ('Alert::Live => "Voltage on circuit - power off"', 'Alert::Live => "电路带电，请先断电"'),
    ('Alert::Dc => "DC voltage here: use DC V?"', 'Alert::Dc => "这里是直流，改用直流 V？"'),
    ('Alert::Ac => "AC voltage here: use AC V?"', 'Alert::Ac => "这里是交流，改用交流 V？"'),
    ('Alert::Fuse => "0 A for 60 s: check the fuse?"', 'Alert::Fuse => "60 秒无电流，检查保险丝？"'),
]
for old, new in PAIRS:
    if t.count(old) != 1:
        raise SystemExit("%r -> %d" % (old[:44], t.count(old)))
    t = t.replace(old, new)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("alert toasts localized")
