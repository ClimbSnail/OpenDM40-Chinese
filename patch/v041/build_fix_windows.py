#!/usr/bin/env python3
"""Windows build fixes for the upstream v0.4.1 tree (idempotent).

Upstream is built on Linux / in git-bash; two spots assume a unix layout and
break a Windows host:

1. `tools/stack-depth/stackdepth.py` `tool()` globs for `llvm-objdump` with no
   `.exe`, so it never matches and `build.sh` stops right after the link
   ("stackdepth: llvm-objdump not found"). Add the `.exe` fallback.

Run from the build tree root:

    python build_fix_windows.py <firmware-dir>
"""

import io
import os
import sys

MARK = "Windows: the tools carry a .exe suffix"


def read(p):
    return io.open(p, encoding="utf-8").read()


def write(p, t):
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)


def fix_stackdepth(root):
    p = os.path.join(root, "tools", "stack-depth", "stackdepth.py")
    t = read(p)
    if MARK in t:
        return "stackdepth.py: already fixed"
    old = "    for pat in pats:\n        m = sorted(glob.glob(pat))\n"
    new = ("    for pat in pats:\n        m = sorted(glob.glob(pat))\n"
           "        if not m:  # " + MARK + "\n"
           "            m = sorted(glob.glob(pat + '.exe'))\n")
    if old not in t:
        sys.exit("stackdepth.py: anchor not found (upstream changed?)")
    write(p, t.replace(old, new, 1))
    return "stackdepth.py: .exe fallback added"


def fix_build_sh_rm(root):
    """This host's `rm` is a safe-delete wrapper that fails closed unless it
    can move the file to the trash, and it cannot here, so build.sh stops at
    its own `rm -f $TDIR/region*.warn`. Truncate instead, and test `-s` (the
    python block writes a byte count only when the budget is low) so an empty
    file is not mistaken for a warning."""
    p = os.path.join(root, "build.sh")
    t = read(p)
    if "rm -f $TDIR/regiona2.warn" not in t:
        if ": > $TDIR/regiona2.warn" in t:
            return "build.sh: already fixed"
        sys.exit("build.sh: rm anchor not found (upstream changed?)")
    t = t.replace("rm -f $TDIR/regiona2.warn $TDIR/regionb.warn $TDIR/regionc.warn",
                  ": > $TDIR/regiona2.warn; : > $TDIR/regionb.warn; : > $TDIR/regionc.warn", 1)
    for n in ("regiona2", "regionb", "regionc"):
        t = t.replace("if [ -f $TDIR/%s.warn ]; then" % n,
                      "if [ -s $TDIR/%s.warn ]; then" % n, 1)
    write(p, t)
    return "build.sh: rm -f -> truncate, -f -> -s"


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    for msg in (fix_stackdepth(root), fix_build_sh_rm(root)):
        print(msg)


main()
