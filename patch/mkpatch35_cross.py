#!/usr/bin/env python3
"""Cross-page tick selection for the gallery.

Ticks used to live in a single u8 for the page on screen, and every page turn
dropped them, because the bits are tile indices: the same slots on the next
page would have looked ticked and a delete would have removed those files
instead.

Now there is one byte per page (`sel: [u8; 4]`), so a tick stays with the file
it was put on. Deleting walks the pages with ticks and rescans each one first,
because only the page on screen has its directory entries in `ents`.

RAM: four bytes instead of one; it fits in the padding the struct already had,
so `_stack_top - __bss_end` is unchanged (20 484 B).

Apply to firmware/src/gallery.rs.
"""

import io
import sys

G = sys.argv[1] + "/gallery.rs"
g = io.open(G, encoding="utf-8").read()


def sub(old, new):
    global g
    if g.count(old) != 1:
        sys.exit("anchor missing: %r" % old[:60])
    g = g.replace(old, new)


sub("""    sel: u8,
    sel_n: u8,
    sel_mode: bool,""",
    """    sel: [u8; 4],
    sel_n: u8,
    sel_mode: bool,""")

sub("            sel: 0,\n            sel_n: 0,", "            sel: [0; 4],\n            sel_n: 0,")

sub("""    fn sel_has(&self, i: usize) -> bool {
        self.sel & (1 << i) != 0
    }""",
    """    fn sel_has(&self, i: usize) -> bool {
        self.sel[(self.page & 3) as usize] & (1 << i) != 0
    }""")

sub("""        let bit = 1u8 << i;
        if self.sel & bit != 0 {
            self.sel &= !bit;""",
    """        let p = (self.page & 3) as usize;
        let bit = 1u8 << i;
        if self.sel[p] & bit != 0 {
            self.sel[p] &= !bit;""")
sub("""        } else {
            self.sel |= bit;
            self.sel_n = self.sel_n.saturating_add(1);""",
    """        } else {
            self.sel[p] |= bit;
            self.sel_n = self.sel_n.saturating_add(1);""")

sub("        self.sel = 0;\n        self.sel_n = 0;\n        self.need |= N_LIST;",
    "        self.sel = [0; 4];\n        self.sel_n = 0;\n        self.need |= N_LIST;")

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

sub("                        self.sel_mode = true;\n                        self.sel = 0;",
    "                        self.sel_mode = true;\n                        self.sel = [0; 4];")

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("ok: cross-page ticks")
