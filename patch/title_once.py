import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub("""    set_page: u8,
    set_frac: u8,
    set_drag0: i16,""",
    """    set_page: u8,
    set_frac: u8,
    set_drag0: i16,
    /// The settings page has to repaint its title bar on the next frame
    /// (first paint, or after something else drew over it).
    set_title: bool,""", "field")

sub("            set_frac: 0,\n            set_drag0: -1,",
    "            set_frac: 0,\n            set_drag0: -1,\n            set_title: true,", "init")

# scrolling redraws only the list once the page has been painted once
sub("ui::settings(top as u8, frac, &all[top..hi], self.set_drag0 < 0);",
    "let wt = self.set_title;\n                self.set_title = false;\n                ui::settings(top as u8, frac, &all[top..hi], wt);", "draw")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

# entering the view asks for a full paint again
P2 = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
s = io.open(P2, encoding="utf-8").read()
OLD = "    fn show(&mut self, v: View, clk: &mut Clock) {"
if s.count(OLD) != 1:
    raise SystemExit("show: %d" % s.count(OLD))
NEW = """    fn show(&mut self, v: View, clk: &mut Clock) {
        if v == View::Settings {
            self.set_title = true;
        }"""
s = s.replace(OLD, NEW)
io.open(P2, "w", encoding="utf-8", newline="\n").write(s)
print("title repaint is now explicit")
