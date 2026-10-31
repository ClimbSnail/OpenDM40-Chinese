import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """        let mut r = set_row_big(i);
        r.y -= frac;
        sf::rbox(r, 8, bg, M_BG);"""
NEW = """        let mut r = set_row_big(i);
        r.y -= frac;
        // The list band ends where the position line starts: the row sliding
        // out of it is cut there instead of overrunning it.
        if r.y + r.h > PAGE_KEY_Y {
            r.h = PAGE_KEY_Y - r.y;
        }
        if r.h < 8 || r.y < PAGE_BAR_H - 4 {
            continue;
        }
        sf::rbox(r, 8, bg, M_BG);"""

if t.count(OLD) != 1:
    raise SystemExit("row draw %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("clip added")
