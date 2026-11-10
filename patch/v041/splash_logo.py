#!/usr/bin/env python3
"""Put the boot wordmark into the v0.4.1 splash (upstream has no picture).

    splash_logo.py --src firmware/src --img patch/splash_img.rs

Three edits, each asserted to hit exactly once, and the whole thing is
idempotent so it can run on an already-patched tree:

1. copy `splash_img.rs` into `firmware/src/`;
2. register it as a submodule of `native` in `native.rs` -- the crate keeps
   every `#[path]` there, so the crate root's module list stays as upstream;
3. call it from `splash::draw` right after the background fill, so the picture
   sits 19 px above "opendm40" (splash.rs `TOP` = 132, `gen_splash_img2.py`
   puts the picture at TOP - H - 19) and the version, "载入中..." and the bar
   keep their offsets.

`splash_img` is only read at boot, so it belongs with the rest of the splash:
`native.rs` submodules are linked into `.cold` (region C), and the pixels are
`.rodata.a2.splash` (region A2, zero-wait).
"""

import argparse
import io
import os
import sys

REG_ANCHOR = '#[path = "splash.rs"]\npub mod splash;\n'
REGISTERED = '#[path = "splash_img.rs"]\npub mod splash_img;\n'
DRAW_ANCHOR = "    lcd::fill_rect(0, 0, lcd::W, lcd::H, BG);\n"
DRAW_CALL = "    super::splash_img::draw();\n"


def read(p):
    return io.open(p, encoding="utf-8").read()


def write(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def one(text, needle, what):
    n = text.count(needle)
    if n != 1:
        sys.exit("%s: expected 1 hit, found %d -- upstream changed, fix the anchor" % (what, n))
    return text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True, help="firmware/src of the build tree")
    p.add_argument("--img", required=True, help="the generated splash_img.rs")
    a = p.parse_args()

    out_img = os.path.join(a.src, "splash_img.rs")
    write(out_img, read(a.img))
    print("wrote    %s" % out_img)

    native = os.path.join(a.src, "native.rs")
    t = read(native)
    if REGISTERED in t:
        print("native.rs: splash_img already registered")
    else:
        one(t, REG_ANCHOR, "native.rs (splash registration)")
        write(native, t.replace(REG_ANCHOR, REG_ANCHOR + REGISTERED))
        print("native.rs: registered splash_img")

    splash = os.path.join(a.src, "splash.rs")
    t = read(splash)
    if DRAW_CALL in t:
        print("splash.rs: draw already calls splash_img")
    else:
        one(t, DRAW_ANCHOR, "splash.rs (draw background fill)")
        write(splash, t.replace(DRAW_ANCHOR, DRAW_ANCHOR + DRAW_CALL))
        print("splash.rs: draw() paints the wordmark")


if __name__ == "__main__":
    main()
