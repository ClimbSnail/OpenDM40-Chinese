import io

G = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
g = io.open(G, encoding="utf-8").read()


def sub(old, new):
    global g
    if g.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (g.count(old), old[:70]))
    g = g.replace(old, new)


# --- nav(): arrows stay put; Cancel/Delete go to the title bar -----------
sub("""        // Select mode reuses the two nav pills, so Cancel / Delete look like
        // buttons; turning pages while selecting is the left / right swipe,
        // which keeps the ticks (they are stored per page).
        let (lt, lo, rt, ro) = if self.sel_mode {
            ("取消", true, "删除", self.sel_n > 0)
        } else {
            ("<", self.page > 0, ">", self.page + 1 < pages)
        };""",
    """        // While selecting, the nav row keeps its page arrows (they page, and
        // the ticks are stored per page); Cancel and Delete move up to the
        // title bar, where Delete is the same red button the viewer uses.
        if self.sel_mode {
            fill((0, 0, 480, BAR_H), BAR);
            sf::glyphs(sf::TEXT22, rect(BACK_X, 0, 110, BAR_H), "< 取消", FG, BAR, 1, 0);
            let c = if self.sel_n > 0 { FG } else { DIM };
            sf::rbox(rect(DEL.0, DEL.1, DEL.2, DEL.3), 6, if self.sel_n > 0 { D_RED } else { M_TILE }, BAR);
            sf::glyphs(sf::TEXT22, rect(DEL.0, DEL.1, DEL.2, DEL.3), "删除", c, if self.sel_n > 0 { D_RED } else { M_TILE }, 8, 0);
        }
        let (lt, lo, rt, ro) = ("<", self.page > 0, ">", self.page + 1 < pages);""")

# --- taps: title bar = Cancel / Delete while selecting -------------------
sub("""                if (p.y as i16) < BAR_H {
                    return Out::Exit;
                }""",
    """                if (p.y as i16) < BAR_H {
                    if !self.sel_mode {
                        return Out::Exit;
                    }
                    if p.x >= DEL_HIT_X {
                        if self.sel_n > 0 {
                            // No confirm box: the gallery's dialog boxes do
                            // not take taps on this unit, and a dead dialog
                            // would strand the screen.
                            self.mode = Mode::Dialog;
                            self.dlg = Dlg::Deleting;
                            self.sel_pending = true;
                            self.need |= N_DEL;
                        }
                    } else {
                        self.leave_sel();
                    }
                    return Out::Stay;
                }""")

# --- taps in the nav row: page arrows again ------------------------------
sub("""                if (p.y as i16) >= NAV_Y - 4 {
                    if self.sel_mode {
                        if (p.x as i16) < PREV_X + NAV_W + 10 {
                            self.leave_sel();
                        } else if (p.x as i16) >= NEXT_X - 10 && self.sel_n > 0 {
                            // No confirm box: the gallery's dialog boxes do
                            // not take taps on this unit, and a dead dialog
                            // would strand the screen.
                            self.mode = Mode::Dialog;
                            self.dlg = Dlg::Deleting;
                            self.sel_pending = true;
                            self.need |= N_DEL;
                        }
                    } else if (p.x as i16) < PREV_X + NAV_W + 10 {
                        self.turn(-1);
                    } else if (p.x as i16) >= NEXT_X - 10 {
                        self.turn(1);
                    } else {""",
    """                if (p.y as i16) >= NAV_Y - 4 {
                    if (p.x as i16) < PREV_X + NAV_W + 10 {
                        self.turn(-1);
                    } else if (p.x as i16) >= NEXT_X - 10 {
                        self.turn(1);
                    } else if self.sel_mode {
                        // Middle does nothing while selecting.
                    } else {""")

# --- leave_sel must repaint the title bar we painted over ----------------
sub("""        self.sel_mode = false;
        self.sel = [0; 4];
        self.sel_n = 0;
        self.need |= N_LIST;""",
    """        self.sel_mode = false;
        self.sel = [0; 4];
        self.sel_n = 0;
        // nav() painted Cancel / Delete over the title bar; redraw the page.
        self.paint |= P_ALL;
        self.need |= N_LIST;""")

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("ok: Delete is the viewer's red button, arrows keep paging")
