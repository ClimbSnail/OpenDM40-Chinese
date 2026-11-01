import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """            } else {
                self.work(&mut io);
            }"""
NEW = """            } else if self.mode != Mode::Dialog {
                // A half-decoded thumbnail would otherwise keep drawing over
                // the confirm box that just came up.
                self.work(&mut io);
            }"""

if t.count(OLD) != 1:
    raise SystemExit("anchor %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("tile decoding stops while a dialog is up")
