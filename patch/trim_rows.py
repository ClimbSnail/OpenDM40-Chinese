import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """        let mut r = set_row_big(i);
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

NEW = """        let mut r = set_row_big(i);
        r.y -= frac;
        // Rows are trimmed at the band edges, never dropped: dropping them
        // left visible gaps at the top and the bottom while scrolling.
        if r.y < PAGE_BAR_H {
            let d = PAGE_BAR_H - r.y;
            if d >= r.h - 6 {
                continue;
            }
            r.y = PAGE_BAR_H;
            r.h -= d;
        }
        if r.y + r.h > PAGE_KEY_Y {
            r.h = PAGE_KEY_Y - r.y;
        }
        if r.h < 6 {
            continue;
        }
        sf::rbox(r, 8, bg, M_BG);"""

if t.count(OLD) != 1:
    raise SystemExit("row clip %d" % t.count(OLD))
t = t.replace(OLD, NEW)

# while scrolling, clear the whole list band (top to bottom of the panel)
OLD2 = """            // Scrolling: only the list band is cleared, the title bar and the
            // position line are left alone (a full clear every frame flickers).
            lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, (PAGE_KEY_Y - PAGE_BAR_H) as u16, M_BG);"""
NEW2 = """            // Scrolling: clear the list band only; the title bar stays put
            // (repainting it every frame flickered).
            lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, (lcd::H as i16 - PAGE_BAR_H) as u16, M_BG);"""
if t.count(OLD2) != 1:
    raise SystemExit("band clear %d" % t.count(OLD2))
t = t.replace(OLD2, NEW2)

# the stepper rows follow the same trim
OLD3 = """            if let Some(v) = vals.get(g - top) {
                let mut r = set_row_big(g - top);
                r.y -= frac;"""
NEW3 = """            if let Some(v) = vals.get(g - top) {
                let mut r = set_row_big(g - top);
                r.y -= frac;
                if r.y < PAGE_BAR_H {
                    continue;
                }"""
if t.count(OLD3) != 1:
    raise SystemExit("stepper %d" % t.count(OLD3))
t = t.replace(OLD3, NEW3)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("rows trimmed, band fully cleared")
