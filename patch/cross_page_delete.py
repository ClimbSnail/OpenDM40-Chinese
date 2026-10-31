import io

G = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
g = io.open(G, encoding="utf-8").read()


def sub(old, new):
    global g
    if g.count(old) != 1:
        raise SystemExit("anchor missing: %r" % old[:60])
    g = g.replace(old, new)


# ---- state: one byte per page (4 pages x 6 tiles = 24 files) ----------
sub("""    /// Batch delete: one bit per tile of the current page, the count, and
    /// whether the bar is in select mode (turning a page clears the ticks).
    sel: u8,
    sel_n: u8,
    sel_mode: bool,""",
    """    /// Batch delete: one bit per tile, one byte per page (4 pages x PER_PAGE),
    /// so ticks survive page turns; plus the total count and the mode flag.
    sel: [u8; 4],
    sel_n: u8,
    sel_mode: bool,""")

sub("            sel: 0,\n            sel_n: 0,", "            sel: [0; 4],\n            sel_n: 0,")

sub("""    fn sel_has(&self, i: usize) -> bool {
        self.sel & (1 << i) != 0
    }

    fn sel_toggle(&mut self, i: usize) {
        let bit = 1u8 << i;
        if self.sel & bit != 0 {
            self.sel &= !bit;
            self.sel_n = self.sel_n.saturating_sub(1);
        } else {
            self.sel |= bit;
            self.sel_n = self.sel_n.saturating_add(1);
        }
    }""",
    """    fn sel_has(&self, i: usize) -> bool {
        self.sel[(self.page & 3) as usize] & (1 << i) != 0
    }

    fn sel_toggle(&mut self, i: usize) {
        let p = (self.page & 3) as usize;
        let bit = 1u8 << i;
        if self.sel[p] & bit != 0 {
            self.sel[p] &= !bit;
            self.sel_n = self.sel_n.saturating_sub(1);
        } else {
            self.sel[p] |= bit;
            self.sel_n = self.sel_n.saturating_add(1);
        }
    }""")

# ---- leaving the mode drops every page's ticks -----------------------
sub("""    fn leave_sel(&mut self) {
        self.sel_mode = false;
        self.sel = 0;
        self.sel_n = 0;
        self.need |= N_LIST;
        self.nav();
    }""",
    """    fn leave_sel(&mut self) {
        self.sel_mode = false;
        self.sel = [0; 4];
        self.sel_n = 0;
        self.need |= N_LIST;
        self.nav();
    }""")

# ---- a page turn keeps the ticks now ---------------------------------
sub("""        // The ticks are per-tile indices, so they would otherwise appear on
        // the same positions of the new page -- and a delete would hit those
        // files instead of the ones that were ticked. Drop them here.
        self.sel = 0;
        self.sel_n = 0;
        self.sel_mode = false;
        self.need |= N_PAGE;""",
    """        // The ticks are stored per page, so they stay with the files that
        // were ticked rather than moving to the same slot of the new page.
        self.need |= N_PAGE;""")

# ---- delete every ticked page ---------------------------------------
start = g.find("    /// Batch delete: every ticked tile of this page, one at a time, the")
end = g.find("    /// Thumbnails, the viewer image or chart: one block.")
if start < 0 or end < start:
    raise SystemExit("delete_selected not found")

new_body = '''    /// Batch delete: every ticked tile, page by page. Pages other than the
    /// one on screen are rescanned first, because only the current page's
    /// directory entries are in `ents`. A busy disk is retried on later
    /// passes; the ticks stay until the file is really gone.
    fn delete_selected(&mut self, disk: &mut dyn BlockDevice) {
        let home = self.page;
        let mut left = 0u8;
        let pages = self.pages();
        for p in 0..pages {
            let idx = (p & 3) as usize;
            if self.sel[idx] == 0 {
                continue;
            }
            if p != self.page {
                let Some(v) = self.v else { continue };
                let mut io = Io::new(disk, v);
                self.page = p;
                self.page_scan(&mut io);
                if (p & 3) as usize != idx {
                    continue;
                }
            }
            let bits = self.sel[idx];
            for k in 0..self.n {
                if bits & (1 << k) == 0 {
                    continue;
                }
                let name = self.ents[k].name;
                let mut kicky = Kicky(disk);
                match csvlog::delete_on(&mut kicky, &name) {
                    Ok(()) => {
                        self.total = self.total.saturating_sub(1);
                        self.sel[idx] &= !(1 << k);
                        self.sel_n = self.sel_n.saturating_sub(1);
                    }
                    // Gone already (a stale listing): count it as done.
                    Err(GErr::NotFound) => {
                        self.sel[idx] &= !(1 << k);
                        self.sel_n = self.sel_n.saturating_sub(1);
                    }
                    Err(_) => left += 1,
                }
            }
        }
        self.page = home;
        if left > 0 && self.del_try < 8 {
            // A busy disk (the host has the volume open, a screenshot or a log
            // commit is running) clears in a pass or two.
            self.del_try += 1;
            self.mode = Mode::Grid;
            self.need |= N_DEL;
            return;
        }
        self.del_try = 0;
        self.sel_pending = false;
        if self.sel_n > 0 {
            // Out of retries: say so instead of leaving the ticks looking done.
            self.sel = [0; 4];
            self.sel_n = 0;
            self.sel_mode = false;
            self.mode = Mode::Grid;
            self.to_grid();
            self.fail("删除失败", 0, 0);
            return;
        }
        self.sel = [0; 4];
        self.sel_mode = false;
        self.mode = Mode::Grid;
        self.to_grid();
    }

'''
g = g[:start] + new_body + g[end:]

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("ok: ticks per page, delete walks every page")
