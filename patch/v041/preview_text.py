#!/usr/bin/env python3
"""Render a string the way the firmware's TEXT22 face would draw it.

No emulator, no hardware: it decodes the generated `stockfont_data.rs` (BIT1)
and repeats `stockfont::layout`'s arithmetic, so a width measured here is the
width on the panel. That answers what a build cannot:

    # does a label fit its box?
    preview_text.py --font-file firmware/src/stockfont_data.rs \
                    --text "信号源轨迹：" --rect 24,163,180,20 --out build/out/t.png

    # what the boot splash will look like
    preview_text.py --font-file ... --splash --logo patch/splash_img.rs \
                    --out build/out/splash.png

BIT1 (`Glyph::alpha`): pixel (x, y) with t <= y < t+ih is bit `x*ih + (y-t)` of
the glyph blob, MSB first, at byte `off`. Placement (`layout`):
y = rect.y + oy + line_h - descent - h - yoff; x advances by `adv + spacing`.
"""

import argparse
import io
import re
import sys

from PIL import Image

ENTRY = re.compile(r"E\((0x[0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(\d+),(\d+)\)")


def rust_bytes(body):
    """Decode the body of a `*b"..."` literal into bytes."""
    out, i, n = bytearray(), 0, len(body)
    while i < n:
        c = body[i]
        if c != "\\":
            out.extend(c.encode("utf-8"))
            i += 1
            continue
        e = body[i + 1]
        if e == "x":
            out.append(int(body[i + 2:i + 4], 16))
            i += 4
        elif e == "\\":
            out.append(0x5C)
            i += 2
        elif e == "n":
            out.append(0x0A)
            i += 2
        elif e == "0":
            out.append(0)
            i += 2
        else:
            i += 2
    return bytes(out)


def load(font_file, name):
    text = io.open(font_file, encoding="utf-8").read()
    fd = re.search(r"pub static %s_FD: FontData = FontData\{line_h:(\d+),descent:(-?\d+)," % name, text)
    if not fd:
        sys.exit("no %s_FD in %s" % (name, font_file))
    line_h, descent = int(fd.group(1)), int(fd.group(2))
    e = re.search(r"pub static %s_E: \[Entry; \d+\] = \[(.*?)\];" % name, text, re.S)
    entries = {}
    for m in ENTRY.finditer(e.group(1)):
        code, off, w, h, adv, yoff, t, ih = (int(m.group(i), 0) for i in range(1, 9))
        entries[code] = (off, w, h, adv, yoff, t, ih)
    # The blob is one long `*b"...";` literal whose body holds `\xNN` escapes
    # and may be wrapped by a backslash-newline, so cut between the first
    # `b"` and the last quote of that static.
    i = text.index("pub static %s_B: " % name)
    seg = text[i:text.index("\npub static", i)]
    body = seg[seg.index('*b"') + 3:seg.rindex('"')]
    return line_h, descent, entries, rust_bytes(body)


def draw_text(img, font, text, rect, align=8, spacing=0, fg=(255, 255, 255)):
    line_h, descent, entries, blob = font
    x0, y0, w, h = rect

    xs, pen, last_w = [], 0, 0
    for ch in text:
        g = entries.get(ord(ch))
        xs.append(pen)
        if g is None:
            pen += line_h
            last_w = line_h
        else:
            pen += (max(g[3], line_h // 3) if ch == " " else g[3]) + spacing
            last_w = g[1]
    if not text:
        return 0
    tw = xs[-1] + last_w

    ox = 0 if align <= 2 else (w - tw if align <= 5 else (w - tw) >> 1)
    oy = 0 if align in (0, 3, 6) else (h - line_h if align in (2, 5, 7) else (h - line_h) >> 1)

    for i, ch in enumerate(text):
        g = entries.get(ord(ch))
        if not g:
            continue
        off, gw, gh, adv, yoff, t, ih = g
        gx = x0 + ox + xs[i]
        gy = y0 + oy + line_h - descent - gh - yoff
        for px in range(gw):
            for py in range(t, t + ih):
                p = px * ih + (py - t)
                byte = blob[off + p // 8] if off + p // 8 < len(blob) else 0
                if byte & (0x80 >> (p & 7)):
                    X, Y = gx + px, gy + py
                    if 0 <= X < img.width and 0 <= Y < img.height:
                        img.putpixel((X, Y), fg)
    return tw


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--font-file", required=True)
    p.add_argument("--font", default="TEXT22")
    p.add_argument("--text")
    p.add_argument("--rect", help="x,y,w,h")
    p.add_argument("--align", type=int, default=8)
    p.add_argument("--spacing", type=int, default=0)
    p.add_argument("--scale", type=int, default=2)
    p.add_argument("--splash", action="store_true", help="compose the boot splash")
    p.add_argument("--logo", help="splash_img.rs to include")
    p.add_argument("--version", default="v0.4.1.01")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    font = load(a.font_file, a.font)

    if a.splash:
        img = Image.new("RGB", (480, 320), (0, 0, 0))
        if a.logo:
            src = io.open(a.logo, encoding="utf-8").read()
            m = re.search(r"static IMG: \[u8; \d+\] = \[(.*?)\];", src, re.S)
            px = [int(x, 16) for x in re.findall(r"0x([0-9A-Fa-f]{2})", m.group(1))]
            W = int(re.search(r"pub const W: i16 = (\d+);", src).group(1))
            H = int(re.search(r"pub const H: i16 = (\d+);", src).group(1))
            X = int(re.search(r"pub const X: i16 = (\d+);", src).group(1))
            Y = int(re.search(r"pub const Y: i16 = (\d+);", src).group(1))
            stride = (W + 7) // 8
            for y in range(H):
                for x in range(W):
                    if px[y * stride + x // 8] & (0x80 >> (x % 8)):
                        img.putpixel((X + x, Y + y), (255, 255, 255))
        a26 = load(a.font_file, "ASCII26")
        dim = (150, 150, 150)
        draw_text(img, a26, "opendm40", (0, 132, 480, 30), 8, 8)      # ASCII26, spacing 8
        draw_text(img, a26, a.version, (0, 164, 480, 30), 8, 8, dim)
        w = draw_text(img, font, "载入中...", (0, 206, 480, 30), 8, 1, dim)
        print("载入中... width: %d px (rect 480)" % w)
        x, y, bw, bh = 160, 246, 160, 8
        for i in range(bw):
            img.putpixel((x + i, y), dim)
            img.putpixel((x + i, y + bh - 1), dim)
        for j in range(bh):
            img.putpixel((x, y + j), dim)
            img.putpixel((x + bw - 1, y + j), dim)
    else:
        x, y, w, h = (int(v) for v in a.rect.split(","))
        img = Image.new("RGB", (w, h), (0, 0, 0))
        tw = draw_text(img, font, a.text, (0, 0, w, h), a.align, a.spacing)
        print("text    : %s" % a.text)
        print("width   : %d px in rect %d%s" % (tw, w, "   <-- OVERFLOW" if tw > w else ""))

    img.resize((img.width * a.scale, img.height * a.scale), Image.NEAREST).save(a.out)
    print("wrote   : %s" % a.out)


if __name__ == "__main__":
    main()
