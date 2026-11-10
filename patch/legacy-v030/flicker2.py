import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()

OLD = "                ui::settings(top as u8, frac, &all[top..hi]);"
NEW = "                ui::settings(top as u8, frac, &all[top..hi], self.set_drag0 < 0);"
print("call sites:", t.count(OLD))
t = t.replace(OLD, NEW)

OLD2 = """            Gesture::Drag(a, b, _) if self.view == View::Settings => {
                if self.set_drag0 < 0 {
                    self.set_drag0 = self.scroll_px();
                }
                self.set_scroll_px(self.set_drag0 + a.y as i16 - b.y as i16);
            }"""
NEW2 = """            Gesture::Drag(a, b, _) if self.view == View::Settings => {
                if self.set_drag0 < 0 {
                    self.set_drag0 = self.scroll_px();
                }
                // One repaint per 6 px: repainting on every drag event made
                // the screen flicker.
                let want = self.set_drag0 + a.y as i16 - b.y as i16;
                if (want - self.scroll_px()).abs() >= 6 {
                    self.set_scroll_px(want);
                }
            }"""
print("drag arm:", t.count(OLD2))
t = t.replace(OLD2, NEW2)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("written")
