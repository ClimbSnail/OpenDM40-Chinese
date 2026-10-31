#!/usr/bin/env python3
"""Batch delete: keep the ticks in one byte instead of a name table.

The name table (16 x 11 B in the Gallery static) grew .bss enough to break the
stack-headroom check (20308 < 20480). A page holds PER_PAGE (6) tiles, so a u8
bitmask covers it; turning a page clears the ticks.

    python mkpatch31.py FIRMWARE_SRC_DIR
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


sub("const PER_PAGE: usize = 6;\n/// Batch delete: how many ticked names fit.\nconst SEL_MAX: usize = 16;",
    "const PER_PAGE: usize = 6;",
    "SEL_MAX")

sub("""    /// Batch delete: ticked names (8.3), count, and whether the bar is in
    /// select mode. Names keep the ticks across page turns.
    sel: [[u8; 11]; SEL_MAX],
    sel_n: u8,
    sel_mode: bool,""",
    """    /// Batch delete: one bit per tile of the current page, the count, and
    /// whether the bar is in select mode (turning a page clears the ticks).
    sel: u8,
    sel_n: u8,
    sel_mode: bool,""",
    "fields")

sub("""            sel: [[0; 11]; SEL_MAX],
            sel_n: 0,
            sel_mode: false,""",
    """            sel: 0,
            sel_n: 0,
            sel_mode: false,""",
    "init")

sub("""    fn sel_has(&self, name: &[u8; 11]) -> bool {
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
    }""",
    """    fn sel_has(&self, i: usize) -> bool {
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
    }

    /// Leave select mode (the ticks stay for the next time).
    fn leave_sel(&mut self) {
        self.sel_mode = false;
        self.sel = 0;
        self.sel_n = 0;
        self.need |= N_LIST;
    }""",
    "helpers")

sub("""                        if self.sel_mode {
                            let e = self.ents[i];
                            self.sel_toggle(e.name);
                            self.need |= N_LIST;
                        } else {""",
    """                        if self.sel_mode {
                            self.sel_toggle(i);
                            self.need |= N_LIST;
                        } else {""",
    "tile tap")

sub("        if self.sel_has(&e.name) {", "        if self.sel_has(i) {", "tile frame check")

sub("""        let mut done = 0u32;
        let mut bad: Option<&'static str> = None;
        let n = self.sel_n as usize;
        for k in 0..n {
            let name = self.sel[k];
            crate::wdt::kick_if_feeding();
            match csvlog::delete_on(disk, &name) {""",
    """        let mut done = 0u32;
        let mut bad: Option<&'static str> = None;
        let mask = self.sel;
        let n = self.n;
        for k in 0..n {
            if mask & (1 << k) == 0 {
                continue;
            }
            let name = self.ents[k].name;
            crate::wdt::kick_if_feeding();
            match csvlog::delete_on(disk, &name) {""",
    "delete loop")

sub("""        self.sel_pending = false;
        self.sel_n = 0;
        self.sel_mode = false;""",
    """        self.sel_pending = false;
        self.sel = 0;
        self.sel_n = 0;
        self.sel_mode = false;""",
    "delete cleanup")

sub("""                    } else {
                        // Middle: enter select mode.
                        self.sel_mode = true;
                        self.sel_n = 0;
                        self.need |= N_LIST;
                    }""",
    """                    } else {
                        // Middle: enter select mode.
                        self.sel_mode = true;
                        self.sel = 0;
                        self.sel_n = 0;
                        self.need |= N_LIST;
                    }""",
    "enter select")

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
sys.stderr.write("done: ticks are a bitmask\n")
