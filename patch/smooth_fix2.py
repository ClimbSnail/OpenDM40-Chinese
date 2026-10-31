import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()
n = 0

# 1) the two new fields
OLD = "            set_page: 0,\n"
NEW = "            set_page: 0,\n            set_frac: 0,\n            set_drag0: -1,\n"
if t.count(OLD) == 1:
    t = t.replace(OLD, NEW)
    n += 1
    print("initializer ok")
else:
    print("initializer matches:", t.count(OLD))

# 2) a public helper for the other module
OLD2 = """    /// First settings row on screen, clamped so the window always fits.
    fn set_top(&self) -> usize {"""
NEW2 = """    /// Sub-row shift the list is drawn with (0 on the last screen).
    pub(crate) fn set_frac_now(&self) -> i16 {
        if self.set_top() + ui::SET_SHOWN >= ui::SETTINGS.len() {
            0
        } else {
            self.set_frac as i16
        }
    }

    /// First settings row on screen, clamped so the window always fits.
    pub(crate) fn set_top(&self) -> usize {"""
if t.count(OLD2) == 1:
    t = t.replace(OLD2, NEW2)
    n += 1
    print("helpers ok")
else:
    print("helper matches:", t.count(OLD2))

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

Q = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app_press.rs"
s = io.open(Q, encoding="utf-8").read()
OLD3 = "let k = ui::settings_hit(y)?;"
if s.count(OLD3) == 1:
    s = s.replace(OLD3, "let k = ui::settings_hit(y, self.set_frac_now())?;")
    io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
    print("press ok")
else:
    print("press matches:", s.count(OLD3))
print("wrote", n)
