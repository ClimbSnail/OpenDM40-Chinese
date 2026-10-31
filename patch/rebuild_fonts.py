#!/usr/bin/env python3
"""Rebuild the two patched fonts in firmware/src/stockfont_data.rs correctly.

Both earlier attempts had the glyphs drawn on a canvas exactly as tall as the
cell, with the baseline on its bottom edge, so the bottom rows of the ink were
cut at render time (TEXT22 came out t=4, ih=18 where the vendor's glyphs are
t=1, ih=20). That is what made the drawn characters look small and their
bottoms clipped on the meter.

There is also no single encoding: the two fonts store a glyph differently.

  TEXT22  h = the cell height (22 for every glyph), t = the ink's first row,
          ih = the ink height, yoff = 0.
          The vendor's hanzi are t=1..2, ih=19..20 -- ink in rows 1..20 of 22.

  F14     h = the ink height, t = 0, and yoff places the ink:
          p.y = r.y + line_h - descent - h - yoff
          (vendor 'M': h=9, yoff=0 -> p.y=2, ink rows 2..10 of 14)

So the ink is rendered on a roomy canvas, then pasted into the cell at a
chosen top row, and each font gets its own encoding.

    python rebuild_fonts.py --pristine SRC --cjk-src CJKSRC --out DST \\
        --txt22-keep keep_cjk.txt --txt22-draw need_glyphs.txt \\
        --f14 鐩稿鏍?"""

import io
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

TTF = "C:\\Windows\\Fonts\\simsun.ttc"
ENT = re.compile(r"E\((0x[0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(\d+),(\d+)\)")


def render(ch, size, cell_h, adv, top):
    """Ink of `ch` pasted into a cell_h x adv grid at row `top`. Returns
    (pixels column-major, ih) or (None, 0) for a blank."""
    canvas = size + 32
    img = Image.new("L", (canvas, canvas), 0)
    ImageDraw.Draw(img).text((4, canvas - 8), ch, font=ImageFont.truetype(TTF, size), fill=255, anchor="ls")
    px = img.load()
    rows = [y for y in range(canvas) if any(px[x, y] >= 110 for x in range(canvas))]
    cols = [x for x in range(canvas) if any(px[x, y] >= 110 for y in range(canvas))]
    if not rows:
        return None, 0
    r0, r1 = rows[0], rows[-1]
    c0, c1 = cols[0], cols[-1]
    ink_h = r1 - r0 + 1
    ink_w = c1 - c0 + 1
    if ink_h > cell_h - top + 1:
        sys.exit("%s: ink %d rows does not fit %d (top %d)" % (ch, ink_h, cell_h, top))
    if ink_w > adv:
        sys.exit("%s: ink %d px wide, advance is %d" % (ch, ink_w, adv))
    # Align by the baseline, not by the top. The vendor's hanzi end on row 20
    # of the 22-row cell (84 of 94 of them); top-aligning instead leaves the
    # shorter characters -- 上 for one -- floating 2 px above their neighbours.
    baseline_src = canvas - 8
    below = baseline_src - r1
    if ink_h >= 18:
        # Full-height characters: pin the ink bottom to row 20, which is where
        # 84 of the vendor's 94 hanzi end. Baseline-relative placement leaves
        # 上 two rows high because its bottom stroke does not overshoot.
        dst_bottom = 20
    else:
        dst_bottom = 19 - below   # 一 / 二 / 三 and friends keep their offset
    dst_top = dst_bottom - ink_h + 1
    if dst_top < 0:
        dst_top = 0
    out = [0] * (adv * cell_h)
    xo = max(0, (adv - ink_w) // 2)
    for y in range(ink_h):
        for x in range(ink_w):
            if px[c0 + x, r0 + y] >= 110:
                out[(xo + x) * cell_h + (dst_top + y)] = 15
    return out, ink_h


def crop(px, w, h):
    ink = [y for y in range(h) if any(px[x * h + y] for x in range(w))]
    if not ink:
        return b"", 0, 0
    top, ih = ink[0], ink[-1] - ink[0] + 1
    bits = [px[x * h + y] for x in range(w) for y in range(top, top + ih)]
    out = bytearray((len(bits) + 7) // 8)
    for p, v in enumerate(bits):
        if v:
            out[p >> 3] |= 0x80 >> (p & 7)
    return bytes(out), top, ih


def uncrop(b, w, h, top, ih):
    return [15 if top <= y < top + ih and b[(x * ih + y - top) >> 3] & (0x80 >> ((x * ih + y - top) & 7)) else 0
            for x in range(w) for y in range(h)]


def load_font(text, name):
    m = re.search(r"pub static %s_E: \[Entry; (\d+)\] = \[(.*?)\];" % name, text, re.S)
    mb = re.search(r'pub static %s_B: \[u8; (\d+)\] = \*b"\\\n(.*?)"\n;' % name, text, re.S)
    if not m or not mb:
        sys.exit("%s not found" % name)
    ents = [(int(a, 16), int(b), int(c), int(d_), int(e), int(f), int(g), int(h))
            for a, b, c, d_, e, f, g, h in ENT.findall(m.group(2))]
    blob = bytes(int(x, 16) for x in re.findall(r"\\x([0-9a-f]{2})", mb.group(2)))
    glyphs = []
    for (code, off, w, h, adv, yoff, tt, ih) in ents:
        glyphs.append([code, w, h, adv, yoff, uncrop(blob[off:], w, h, tt, ih)])
    return glyphs


def emit(text, name, glyphs):
    glyphs.sort(key=lambda g: g[0])
    blob = bytearray()
    ents = []
    for (code, w, h, adv, yoff, px) in glyphs:
        # Re-derive the byte encoding from the pixels.
        enc, tt, ih = crop(px, w, h)
        # Two encodings (see the module docstring): when the record's height
        # already equals the ink height (F14), keep t = 0 and h = ih; when it
        # is the cell height (TEXT22), keep h and carry the ink's first row
        # in t.
        if h == ih:
            h_out, t_out = ih, 0
        else:
            h_out, t_out = h, tt
        ents.append((code, len(blob), w, h_out, adv, yoff, t_out, ih))
        blob += enc

    lines, line = [], "    "
    for (code, off, w, h, adv, yoff, tt, ih) in ents:
        cell = "E(0x%X,%d,%d,%d,%d,%d,%d,%d)," % (code, off, w, h, adv, yoff, tt, ih)
        if len(line) + len(cell) > 116:
            lines.append(line)
            line = "    "
        line += cell
    if line.strip():
        lines.append(line)
    e_block = "pub static %s_E: [Entry; %d] = [\n%s\n];" % (name, len(ents), "\n".join(lines))
    esc = "".join("\\x%02x" % b for b in blob)
    bl = ['pub static %s_B: [u8; %d] = *b"\\' % (name, len(blob))]
    for j in range(0, len(esc), 128):
        bl.append(esc[j:j + 128] + ("\\" if j + 128 < len(esc) else '"'))
    bl.append(";")
    b_block = "\n".join(bl)

    text = re.sub(r"pub static %s_E: \[Entry; \d+\] = \[.*?\];" % name, lambda _: e_block, text, flags=re.S)
    text = re.sub(r'pub static %s_B: \[u8; \d+\] = \*b"\\\n.*?"\n;' % name, lambda _: b_block, text, flags=re.S)
    sys.stderr.write("%s: %d glyphs, blob %d B\n" % (name, len(ents), len(blob)))
    return text


def main():
    argv = sys.argv[1:]

    def opt(n, d=None):
        return argv[argv.index(n) + 1] if n in argv else d

    pristine = io.open(opt("--pristine"), encoding="utf-8").read()
    cjksrc = io.open(opt("--cjk-src"), encoding="utf-8").read()
    out = opt("--out")
    keep_txt = io.open(opt("--txt22-keep"), encoding="utf-8").read().strip()
    draw_txt = io.open(opt("--txt22-draw"), encoding="utf-8").read().strip()
    f14_chars = opt("--f14", "")
    ascii_keep_file = opt("--ascii-keep")
    keep_ascii = None
    if ascii_keep_file:
        keep_ascii = set(io.open(ascii_keep_file, encoding="utf-8").read())

    # ---------------- TEXT22: cell 22, ink top row 1, yoff 0 ----------
    text = pristine
    g = load_font(text, "TEXT22")
    if keep_ascii is not None:
        before = len(g)
        g = [x for x in g if x[0] >= 0x80 or chr(x[0]) in keep_ascii]
        sys.stderr.write("TEXT22: Latin glyphs %d -> %d (dropped %d)\n"
                         % (before - sum(1 for x in g if x[0] >= 0x80), 0, 0))
    src = {x[0]: x for x in load_font(cjksrc, "TEXT22")}
    have = set(x[0] for x in g)
    for ch in keep_txt:
        code = ord(ch)
        if code in src and code not in have:
            g.append([src[code][0], 22, 22, 22, 0, src[code][5]])
            have.add(code)
    added = 0
    for ch in draw_txt:
        code = ord(ch)
        if code in have:
            continue
        px, ih = render(ch, 22, 22, 22, 1)
        if px is None:
            continue
        g.append([code, 22, 22, 22, 0, px])
        have.add(code)
        added += 1
    sys.stderr.write("TEXT22: %d drawn (ink top 1)\n" % added)
    text = emit(text, "TEXT22", g)

    # ---------------- F14: h = ink height, t = 0, yoff places it ------
    if f14_chars:
        g = load_font(text, "F14")
        have = set(x[0] for x in g)
        lh, desc = 14, 3
        added = 0
        for ch in f14_chars:
            code = ord(ch)
            if code in have:
                continue
            px, ih = render(ch, 11, 14, 11, 0)
            if px is None:
                continue
            # ink rows 1.. of the 14 px line: p.y = lh - desc - h - yoff = 1
            yoff = lh - desc - ih - 1
            g.append([code, 11, ih, 11, yoff, px])
            have.add(code)
            added += 1
            sys.stderr.write("  F14 %s: ih=%d yoff=%d -> ink rows 1..%d\n" % (ch, ih, yoff, ih))
        text = emit(text, "F14", g)
        sys.stderr.write("F14: %d drawn\n" % added)

    io.open(out, "w", encoding="utf-8", newline="\n").write(text)
    sys.stderr.write("wrote %s\n" % out)


main()

