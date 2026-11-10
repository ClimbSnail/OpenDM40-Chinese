#!/usr/bin/env python3
"""Feed the watchdog inside a long delete, and drop the BMP-only restriction.

Deleting a file walks its FAT chain block by block. One 300 KB screenshot is
hundreds of flash accesses, and the only kicks were *between* files -- so a
single delete that ran long enough tripped the watchdog, which reset the meter
mid-operation (DBG:BOOT? reporting WDT_RETRY). That matches the "sometimes"
behaviour: small or fewer files finished in time.

Fix: wrap the disk in an adapter that kicks before every block access, and use
it for the delete. The trait's shape is copied from msc::BlockDevice.
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


# ---- 1. the kicking adapter -----------------------------------------
sub("""    /// Batch delete: every ticked tile of this page, one at a time, the""",
    """    /// `BlockDevice` that feeds the watchdog before each access, so a long
    /// FAT chain walk cannot outrun the FWDGT.
    #[cfg_attr(target_os = "none", allow(dead_code))]
    struct Kicky<'a>(&'a mut dyn BlockDevice);

    impl BlockDevice for Kicky<'_> {
        fn present(&self) -> bool {
            self.0.present()
        }
        fn block_size(&self) -> u32 {
            self.0.block_size()
        }
        fn block_count(&self) -> u32 {
            self.0.block_count()
        }
        fn read_block(&mut self, lba: u32, buf: &mut [u8]) -> bool {
            crate::wdt::kick_if_feeding();
            self.0.read_block(lba, buf)
        }
        fn write_block(&mut self, lba: u32, buf: &[u8]) -> bool {
            crate::wdt::kick_if_feeding();
            self.0.write_block(lba, buf)
        }
        fn read_only(&self) -> bool {
            self.0.read_only()
        }
    }

    /// Batch delete: every ticked tile of this page, one at a time, the""",
    "adapter")

# ---- 2. use it, and delete every kind again --------------------------
sub("""            // Only screenshots: deleting a .DLG record has hit the watchdog
            // (WDT_RETRY) on this unit, so those are left alone until the
            // csvlog delete path is understood.
            if self.ents[k].kind != Kind::Bmp {
                continue;
            }
            let name = self.ents[k].name;
            crate::wdt::kick_if_feeding();
            if csvlog::delete_on(disk, &name).is_ok() {""",
    """            let name = self.ents[k].name;
            let mut kicky = Kicky(disk);
            if csvlog::delete_on(&mut kicky, &name).is_ok() {""",
    "delete call")

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
sys.stderr.write("done: watchdog fed per block access, BMP-only restriction dropped\n")
