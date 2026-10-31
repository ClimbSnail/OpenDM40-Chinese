#!/usr/bin/env python3
"""Batch delete in the gallery: tick tiles, delete them all at once.

Selection is keyed by 8.3 name, so it survives page turns; up to SEL_MAX.

  * the middle of the bottom bar enters select mode (where "Page i of n" is)
  * in select mode: left pill = 取消, right pill = 删除 (needs one tick)
  * a tap on a tile toggles its tick instead of opening it
  * ticking paints a frame round the thumbnail
  * 删除 opens a confirm; confirming deletes every ticked name in one pass

    python mkpatch30.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
G = os.path.join(SRC, "gallery.rs")

g = io.open(G, encoding="utf-8").read()


def sub(old, new, label):
    global g
    n = g.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    g = g.replace(old, new)


# ---- 1. state --------------------------------------------------------
sub("const PER_PAGE: usize = 6;",
    "const PER_PAGE: usize = 6;\n/// Batch delete: how many ticked names fit.\nconst SEL_MAX: usize = 16;",
    "SEL_MAX")

sub("""    job: Job,
}""",
    """    job: Job,
    /// Batch delete: ticked names (8.3), count, and whether the bar is in
    /// select mode. Names keep the ticks across page turns.
    sel: [[u8; 11]; SEL_MAX],
    sel_n: u8,
    sel_mode: bool,
    /// The running delete was started by the select mode.
    sel_pending: bool,
}""",
    "fields")

sub("""            mode: Mode::Grid,""",
    """            mode: Mode::Grid,
            sel: [[0; 11]; SEL_MAX],
            sel_n: 0,
            sel_mode: false,
            sel_pending: false,""",
    "init")

# ---- 2. the dialog state --------------------------------------------
sub("""enum Dlg {
    Delete,""",
    """enum Dlg {
    Delete,
    /// Batch delete confirm (created from the select mode).
    DelSel,""",
    "dlg variant")

# ---- 3. helpers ------------------------------------------------------
sub("""    fn pages(&self) -> u32 {""",
    """    fn sel_has(&self, name: &[u8; 11]) -> bool {
        self.sel[..self.sel_n as usize].iter().any(|n| n == name)
    }

    fn sel_toggle(&mut self, name: [u8; 11]) {
        if let Some(k) = self.sel[..self.sel_n as usize].iter().position(|n| *n == name) {
            let n = self.sel_n as usize;
            for j in k..n - 1 {
                self.sel[j] = self.sel[j + 1];
            }
            self.sel_n -= 1;
        } else if (self.sel_n as usize) < SEL_MAX {
            self.sel[self.sel_n as usize] = name;
            self.sel_n += 1;
        }
    }

    /// Leave select mode (the ticks stay for the next time).
    fn leave_sel(&mut self) {
        self.sel_mode = false;
        self.sel_n = 0;
        self.need |= N_LIST;
    }

    fn pages(&self) -> u32 {""",
    "helpers")

# ---- 4. the bottom bar ----------------------------------------------
sub("""        let pages = self.pages();
        for (x, txt, on) in [(PREV_X, "< Prev", self.page > 0), (NEXT_X, "Next >", self.page + 1 < pages)] {""",
    """        let pages = self.pages();
        let (lt, lo, rt, ro) = if self.sel_mode {
            ("取消", true, "删除", self.sel_n > 0)
        } else {
            ("< Prev", self.page > 0, "Next >", self.page + 1 < pages)
        };
        for (x, txt, on) in [(PREV_X, lt, lo), (NEXT_X, rt, ro)] {""",
    "nav pills")

sub("""        let mut t = Tb::new();
        match self.busy {
            Some(_) => t.s("Disk busy"),
            None => {
                t.s("Page ");""",
    """        let mut t = Tb::new();
        match self.busy {
            Some(_) => t.s("磁盘忙"),
            None if self.sel_mode => {
                t.s("已选 ");
                t.u(self.sel_n as u32);
            }
            None => {
                t.s("第 ");
                t.u(self.page + 1);
                t.s(" / ");
                t.u(pages);
                t.s(" 页");""",
    "nav middle")

# ---- 5. taps ---------------------------------------------------------
sub("""                if (p.y as i16) >= NAV_Y - 4 {
                    if (p.x as i16) < PREV_X + NAV_W + 10 {
                        self.turn(-1);
                    } else if (p.x as i16) >= NEXT_X - 10 {
                        self.turn(1);
                    }
                    return Out::Stay;
                }""",
    """                if (p.y as i16) >= NAV_Y - 4 {
                    if self.sel_mode {
                        if (p.x as i16) < PREV_X + NAV_W + 10 {
                            self.leave_sel();
                        } else if (p.x as i16) >= NEXT_X - 10 && self.sel_n > 0 {
                            self.mode = Mode::Dialog;
                            self.dlg = Dlg::DelSel;
                            self.paint |= P_DLG;
                        }
                    } else if (p.x as i16) < PREV_X + NAV_W + 10 {
                        self.turn(-1);
                    } else if (p.x as i16) >= NEXT_X - 10 {
                        self.turn(1);
                    } else {
                        // Middle: enter select mode.
                        self.sel_mode = true;
                        self.sel_n = 0;
                        self.need |= N_LIST;
                    }
                    return Out::Stay;
                }""",
    "nav taps")

sub("""                    if (x..x + TILE_W).contains(&(p.x as i16)) && (y..y + TILE_H).contains(&(p.y""",
    """                    if (x..x + TILE_W).contains(&(p.x as i16)) && (y..y + TILE_H).contains(&(p.y""",
    "tile hit anchor")

sub("""                        self.view(self.page * PER_PAGE as u32 + i as u32, self.ents[i], false);
                        break;""",
    """                        if self.sel_mode {
                            let e = self.ents[i];
                            self.sel_toggle(e.name);
                            self.need |= N_LIST;
                        } else {
                            self.view(self.page * PER_PAGE as u32 + i as u32, self.ents[i], false);
                        }
                        break;""",
    "tile tap")

sub("""                Dlg::Info(..) if inside(OK_BTN, p.x, p.y) => self.close_dialog(),""",
    """                Dlg::DelSel => match crate::dialog::power_off_hit(p.x, p.y) {
                    Some(true) => {
                        self.dlg = Dlg::Deleting;
                        self.sel_pending = true;
                        self.need |= N_DEL;
                    }
                    Some(false) => self.close_dialog(),
                    None => {}
                },
                Dlg::Info(..) if inside(OK_BTN, p.x, p.y) => self.close_dialog(),""",
    "dialog tap")

# ---- 6. run the batch ------------------------------------------------
sub("""        if self.mode != Mode::Dialog || self.dlg != Dlg::Deleting {
            return;
        }
        crate::wdt::kick_if_feeding();""",
    """        if self.mode != Mode::Dialog || self.dlg != Dlg::Deleting {
            return;
        }
        if self.sel_pending {
            self.delete_selected(disk);
            return;
        }
        crate::wdt::kick_if_feeding();""",
    "delete dispatch")

sub("""    /// Thumbnails, the viewer image or chart: one block.""",
    """    /// Batch delete: every ticked name, one at a time, watchdog fed between.
    /// Refreshes the grid afterwards; a failure names the file in the dialog.
    fn delete_selected(&mut self, disk: &mut dyn BlockDevice) {
        let mut done = 0u32;
        let mut bad: Option<&'static str> = None;
        let n = self.sel_n as usize;
        for k in 0..n {
            let name = self.sel[k];
            crate::wdt::kick_if_feeding();
            match csvlog::delete_on(disk, &name) {
                Ok(()) => {
                    done += 1;
                    self.total = self.total.saturating_sub(1);
                }
                Err(GErr::NotFound) => done += 1,
                Err(_) => {
                    bad = Some("删除失败");
                    break;
                }
            }
            crate::wdt::kick_if_feeding();
        }
        self.sel_pending = false;
        self.sel_n = 0;
        self.sel_mode = false;
        self.job.stats = false;
        self.mode = Mode::Grid;
        self.need |= N_LIST | N_FIND;
        match bad {
            Some(m) => {
                self.dlg = Dlg::Info("删除出错", m);
                self.mode = Mode::Dialog;
                self.paint |= P_DLG;
            }
            None => {
                let _ = done;
                if self.total == 0 {
                    self.to_grid();
                }
            }
        }
    }

    /// Thumbnails, the viewer image or chart: one block.""",
    "delete_selected")

# ---- 7. draw the confirm --------------------------------------------
sub("""            Dlg::Delete | Dlg::Deleting => {""",
    """            Dlg::DelSel => {
                let mut t = Tb::new();
                t.s("删除所选的 ");
                t.u(self.sel_n as u32);
                t.s(" 个文件？");
                dialog_box(t.str(), "删除后无法恢复", Some("删除"))
            }
            Dlg::Delete | Dlg::Deleting => {""",
    "confirm draw")

# ---- 8. ticked tiles get a frame ------------------------------------
sub("""        let e = self.ents[i];
        sf::rbox(rect(x, y, TILE_W, TILE_H), 6, M_TILE, M_BG);""",
    """        let e = self.ents[i];
        sf::rbox(rect(x, y, TILE_W, TILE_H), 6, M_TILE, M_BG);
        if self.sel_has(&e.name) {
            // Ticked: a bright frame round the thumbnail.
            for k in 0..3 {
                sf::frame(rect(x + k, y + k, TILE_W - 2 * k, TILE_H - 2 * k), M_ACCENT);
            }
        }""",
    "tick frame")

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
sys.stderr.write("done: batch delete wired\n")
