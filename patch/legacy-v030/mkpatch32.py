#!/usr/bin/env python3
"""Slim the batch delete so it fits, and put the linker rules back.

Region C had 3,928 B free against a 4 KiB floor. Rather than shuffling cold
functions around (each one drags its callees), this trims the new code: the
per-file error dialog and the counters go, and every ticked name is deleted in
one loop. The confirm dialog keeps its own text.

    python mkpatch32.py FIRMWARE_SRC_DIR LINKER_SCRIPT
"""

import io
import os
import sys

SRC, LINK = sys.argv[1], sys.argv[2]

# ---- linker: uid::init back into .cold -------------------------------
l = io.open(LINK, encoding="utf-8").read()
if "uid4init" not in l:
    anchor = "        *(.text.*8opendm406ad2exp*);"
    if anchor not in l:
        sys.exit("cold anchor not found")
    l = l.replace(anchor, "        *(.text.*8opendm403uid4init*);\n" + anchor)
    io.open(LINK, "w", encoding="utf-8", newline="\n").write(l)
    print("linker rule restored")

# ---- gallery: a leaner loop -----------------------------------------
G = os.path.join(SRC, "gallery.rs")
g = io.open(G, encoding="utf-8").read()

start = g.find("    /// Batch delete: every ticked name, one at a time, watchdog fed between.")
end = g.find("    /// Thumbnails, the viewer image or chart: one block.")
if start < 0 or end < start:
    sys.exit("delete_selected block not found")

new = '''    /// Batch delete: every ticked tile of this page, one at a time, the
    /// watchdog fed in between. The grid is rescanned afterwards.
    fn delete_selected(&mut self, disk: &mut dyn BlockDevice) {
        let mask = self.sel;
        let n = self.n;
        for k in 0..n {
            if mask & (1 << k) == 0 {
                continue;
            }
            let name = self.ents[k].name;
            crate::wdt::kick_if_feeding();
            if csvlog::delete_on(disk, &name).is_ok() {
                self.total = self.total.saturating_sub(1);
            }
        }
        self.sel_pending = false;
        self.sel = 0;
        self.sel_n = 0;
        self.sel_mode = false;
        self.mode = Mode::Grid;
        self.job.stats = false;
        self.need |= N_LIST | N_FIND;
        if self.total == 0 {
            self.to_grid();
        }
    }

'''
g = g[:start] + new + g[end:]
io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("delete_selected slimmed")
