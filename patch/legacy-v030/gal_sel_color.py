import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()

OLD = """        sf::rbox(b, 6, if self.sel_mode { SEL_FG } else { M_TILE }, M_BG);
        sf::glyphs(sf::TEXT22, b, "\u591a\u9009", if self.sel_mode { M_BG } else { FG }, if self.sel_mode { SEL_FG } else { M_TILE }, 8, 0);"""
NEW = """        // Same look as the page arrows: no highlight colour.
        sf::rbox(b, 6, M_TILE, M_BG);
        sf::glyphs(sf::TEXT22, b, "\u591a\u9009", FG, M_TILE, 8, 0);"""

if t.count(OLD) != 1:
    raise SystemExit("button colours %d" % t.count(OLD))
t = t.replace(OLD, NEW)
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("multi-select button uses the arrow colours")
