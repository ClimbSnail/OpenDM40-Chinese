import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# rows tile the pitch, so repainting them covers the band
sub("const SB_H: i16 = 42;", "const SB_H: i16 = 46;", "SB_H")
sub("pub const SET_DRAWN: usize = SET_SHOWN + 1;",
    "pub const SET_DRAWN: usize = SET_SHOWN;", "SET_DRAWN")
sub("pub const SET_SHOWN: usize = 5;",
    "pub const SET_SHOWN: usize = 5;\n/// Rows moved per swipe.\npub const SET_SWIPE_ROWS: i16 = 3;", "SET_SHOWN")

# no clear while scrolling: the five tiled rows cover the band
OLD = """        } else {
            // Scrolling: clear the list band only; the title bar stays put
            // (repainting it every frame flickered).
            lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, (lcd::H as i16 - PAGE_BAR_H) as u16, M_BG);
        }"""
NEW = """        }
        // No clear while scrolling: the rows tile the whole pitch, so
        // redrawing them covers the band. Clearing first is what flickered."""
sub(OLD, NEW, "clear")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()
for old, new in [
    ("self.set_scroll(self.set_page as i16 + 1);",
     "self.set_scroll(self.set_page as i16 + ui::SET_SWIPE_ROWS);"),
    ("self.set_scroll(self.set_page as i16 - 1);",
     "self.set_scroll(self.set_page as i16 - ui::SET_SWIPE_ROWS);"),
]:
    if t.count(old) != 1:
        raise SystemExit("app %d: %r" % (t.count(old), old[:40]))
    t = t.replace(old, new)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("done")
