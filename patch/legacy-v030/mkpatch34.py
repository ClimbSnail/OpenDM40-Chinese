#!/usr/bin/env python3
"""Move the Kicky adapter from inside `impl Gallery` to module scope."""

import io
import os
import sys

SRC = sys.argv[1]
G = os.path.join(SRC, "gallery.rs")
g = io.open(G, encoding="utf-8").read()

start = g.find("    /// `BlockDevice` that feeds the watchdog before each access")
end = g.find("    /// Batch delete: every ticked tile of this page, one at a time, the")
if start < 0 or end < start:
    sys.exit("adapter block not found")
block = g[start:end]
g = g[:start] + g[end:]

# de-indent by 4 and place before `pub struct Gallery {`
lines = [l[4:] if l.startswith("    ") else l for l in block.split("\n")]
adapter = "\n".join(lines)

anchor = "pub struct Gallery {"
if anchor not in g:
    sys.exit("struct Gallery not found")
g = g.replace(anchor, adapter + anchor, 1)

io.open(G, "w", encoding="utf-8", newline="\n").write(g)
print("adapter moved to module scope")
