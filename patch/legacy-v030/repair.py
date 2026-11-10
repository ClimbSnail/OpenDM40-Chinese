import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """            // ... and follows the finger while it stays down.
            // Dragging the list was tried and reverted: one row per swipe is
            // what the owner wants (no live follow).
                // One repaint per 6 px: repainting on every drag event made
                // the screen flicker.
                let want = self.set_drag0 + a.y as i16 - b.y as i16;
                if (want - self.scroll_px()).abs() >= 6 {
                    self.set_scroll_px(want);
                }
            }
            Gesture::Up(_) | Gesture::Cancel if self.view == View::Settings => {
                self.set_drag0 = -1;
            }
"""

NEW = """            // Dragging the list was tried and reverted: one row per swipe is
            // what the owner wants, no live following.
"""

if t.count(OLD) != 1:
    raise SystemExit("damaged block %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("repaired")
