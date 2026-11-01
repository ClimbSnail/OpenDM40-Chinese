import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# the middle of the nav row is a named button now, not a bare count
sub("""        let mut t = Tb::new();
        match self.busy {
            Some(_) => t.s("磁盘忙"),
            None if self.sel_mode => {
                // The count alone: the pills already say what the mode is.
                t.u(self.sel_n as u32);
                t.s(" ");
            }
            None => {
                // Plain digits: every extra hanzi costs 64 B of region B.
                t.u(self.page + 1);
                t.s(" / ");
                t.u(pages);
            }
        }
        let mid = rect(PREV_X + NAV_W + 6, NAV_Y, NEXT_X - PREV_X - NAV_W - 12, NAV_H);
        if self.sel_mode {
            // TEXT22: the small font has no hanzi.
            sf::glyphs(sf::TEXT22, mid, t.str(), FG, M_BG, 8, 0);
        } else {
            small(mid, t.str(), FG, M_BG, 8);
        }""",
    """        let mut t = Tb::new();
        match self.busy {
            Some(_) => t.s("磁盘忙"),
            None => {
                // Plain digits: every extra hanzi costs 64 B of region B.
                t.u(self.page + 1);
                t.s(" / ");
                t.u(pages);
            }
        }
        let _ = pages;
        let mid = rect(PREV_X + NAV_W + 6, NAV_Y, NEXT_X - PREV_X - NAV_W - 12, NAV_H);
        // Page digits on the left of the button, the multi-select button on
        // the right of them.
        small(rect(mid.x, mid.y, 90, mid.h), t.str(), if self.busy.is_some() { FG } else { DIM }, M_BG, 1);
        let bx = mid.x + 100;
        let b = rect(bx, NAV_Y, mid.w - 100, NAV_H);
        sf::rbox(b, 6, if self.sel_mode { SEL_FG } else { M_TILE }, M_BG);
        sf::glyphs(sf::TEXT22, b, "多选", if self.sel_mode { M_BG } else { FG }, if self.sel_mode { SEL_FG } else { M_TILE }, 8, 0);""",
    "nav button")

# tapping the middle toggles the mode
sub("""                    } else if self.sel_mode {
                        // Middle does nothing while selecting.
                    } else {""",
    """                    } else if self.sel_mode {
                        self.leave_sel();
                    } else {""",
    "middle tap")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("nav middle is a 多选 button now")
