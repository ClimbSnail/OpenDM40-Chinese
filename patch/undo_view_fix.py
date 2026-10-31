import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """        // The body is drawn from the decode job, and that job only starts on
        // N_CUR: without this the viewer showed its title bar over whatever
        // frame was already on the panel and never loaded the file.
        self.need |= N_CUR;
"""
print("found:", t.count(OLD))
t = t.replace(OLD, "")
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("reverted")
