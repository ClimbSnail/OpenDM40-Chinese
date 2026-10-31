import io

G = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
g = io.open(G, encoding="utf-8").read()

old = """    fn delete_selected(&mut self, disk: &mut dyn BlockDevice) {
        let home = self.page;"""
new = """    fn delete_selected(&mut self, disk: &mut dyn BlockDevice) {
        // page_scan stops before it writes `ents` unless the mode is Grid, and
        // the batch runs with the dialog up: without this the rescan of the
        // second page had no effect and the loop kept deleting the first
        // page's (already gone) names, clearing their ticks as "not found".
        self.mode = Mode::Grid;
        let home = self.page;"""
if g.count(old) != 1:
    raise SystemExit("delete_selected head not found")
g = g.replace(old, new)

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("ok: mode set to Grid before the rescan")
