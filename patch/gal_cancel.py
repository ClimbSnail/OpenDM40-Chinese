import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """    fn close_dialog(&mut self) {
        self.mode = Mode::View;"""
NEW = """    fn close_dialog(&mut self) {
        if self.dlg == Dlg::DelSel {
            // This one came from the grid: go back there, ticks kept, instead
            // of dropping into the viewer with an empty `cur`.
            self.mode = Mode::Grid;
            self.paint |= P_ALL;
            self.need |= N_PAGE;
            return;
        }
        self.mode = Mode::View;"""

if t.count(OLD) != 1:
    raise SystemExit("anchor %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("cancel from DelSel returns to the grid")
