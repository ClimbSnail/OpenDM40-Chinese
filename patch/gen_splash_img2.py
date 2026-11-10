"""Generate the boot splash bitmap (`splash_img.rs`) from a wordmark.

Renders the text with a bold system font, crops to the ink box, thresholds it
to 1 bpp and writes the Rust module. The old version of this script cropped a
JPG at `F:\\desk\\study\\DM40A\\loge\\xingyan_1.jpg`, a drive that no longer
exists, so the picture came from nowhere and could not be changed.

    python patch/gen_splash_img2.py                      # "Snail", bold, 58 px
    python patch/gen_splash_img2.py --text Snail --size 52 --preview build/out/snail.png

Layout: the splash draws "opendm40" at y = TOP (132), the version, "载入中..."
and the bar below it (`splash.rs`); the picture sits LOGO_GAP (19) px above
TOP, and X is centred: X = (480 - W) / 2, Y = TOP - H - 19. With TOP = 132 the
whole block (picture 66 .. 113, text 132 .. 253) is centred on the 320 px
panel, 66 px of margin above and below.

Budget: the pixels live in region A2 (`.rodata.a2.splash`, zero-wait flash,
2,324 bytes free at the v0.4.1.00 build), MSB first, stride = (W + 7) / 8, no
row padding -- the same packing `splash_img::draw` walks.
"""

import argparse
import io
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SCREEN_W, SCREEN_H = 480, 320
TEXT_TOP = 132           # splash.rs: const TOP, first line of text
LOGO_GAP = 19            # px between the picture's bottom and TEXT_TOP
A2_FREE = 2324           # region A2 free at the v0.4.1.01 build

FONTS = [
    r"C:\Windows\Fonts\msyhbd.ttc",     # Microsoft YaHei Bold
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",     # SimHei
    r"C:\Windows\Fonts\arialbd.ttf",
]

RUST = '''//! Boot splash picture: the "{text}" wordmark, {w} x {h}, 1 bpp (MSB first,
//! {stride} bytes per row, no padding). {bytes} bytes of pixels.
//!
//! The bitmap lives in **region A2** (`.rodata.a2.splash`, zero-wait flash,
//! {free} bytes free); the blit loop is ordinary code in region B. Drawn once
//! by `splash::draw`; nothing here runs after boot.
//!
//! Regenerate with `patch/gen_splash_img2.py` (renders the text with a bold
//! system font -- no source picture to lose).

use crate::lcd;
use crate::ui::{{BG, FG}};

/// Picture width and height in pixels, and its top-left corner.
pub const W: i16 = {w};
pub const H: i16 = {h};
pub const X: i16 = {x};
pub const Y: i16 = {y};

#[link_section = ".rodata.a2.splash"]
static IMG: [u8; {bytes}] = [
{body}
];

/// Paint the picture: clear its box, then one `fill_rect` per run of set
/// bits (a few hundred calls, well under a millisecond).
pub fn draw() {{
    lcd::fill_rect(X as u16, Y as u16, W as u16, H as u16, BG);
    let stride = (W as usize + 7) / 8;
    for row in 0..H as usize {{
        let base = row * stride;
        let mut x = 0usize;
        while x < W as usize {{
            if IMG[base + x / 8] & (0x80 >> (x % 8)) == 0 {{
                x += 1;
                continue;
            }}
            let start = x;
            while x < W as usize && IMG[base + x / 8] & (0x80 >> (x % 8)) != 0 {{
                x += 1;
            }}
            let (px, py) = ((X as usize + start) as u16, (Y as usize + row) as u16);
            lcd::fill_rect(px, py, (x - start) as u16, 1, FG);
        }}
    }}
}}
'''


def pick_font(explicit):
    if explicit:
        return explicit
    for f in FONTS:
        if os.path.exists(f):
            return f
    sys.exit("no bold font found; pass --font")


def render(text, font_path, size, threshold):
    """Ink box of `text` as a 1-bit image, cropped to the pixels that are set."""
    font = ImageFont.truetype(font_path, size)
    pad = size
    canvas = Image.new("L", (pad * 2 + size * len(text), pad * 2 + size * 2), 0)
    ImageDraw.Draw(canvas).text((pad, pad), text, font=font, fill=255, anchor="lt")
    box = canvas.getbbox()
    if box is None:
        sys.exit("nothing rendered -- bad font/text")
    img = canvas.crop(box)
    return img.point(lambda p: 255 if p > threshold else 0).convert("1")


def pack(bw, w, h):
    stride = (w + 7) // 8
    data = bytearray()
    for y in range(h):
        for bx in range(stride):
            byte = 0
            for bit in range(8):
                x = bx * 8 + bit
                if x < w and bw.getpixel((x, y)):
                    byte |= 0x80 >> bit
            data.append(byte)
    assert len(data) == stride * h, (len(data), stride, h)
    return data, stride


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--text", default="Snail")
    p.add_argument("--font", help="TTF/TTC to use (default: the first bold font found)")
    p.add_argument("--size", type=int, default=58, help="point size")
    p.add_argument("--threshold", type=int, default=110, help="0-255, above = ink")
    p.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "splash_img.rs"))
    p.add_argument("--preview", help="write a PNG of the bitmap here")
    a = p.parse_args()

    font_path = pick_font(a.font)
    bw = render(a.text, font_path, a.size, a.threshold)
    w, h = bw.size

    if h > TEXT_TOP - 8:
        sys.exit("picture is %d px tall, the band above the text is %d px: use a smaller --size"
                 % (h, TEXT_TOP - 8))
    if w > SCREEN_W - 16:
        sys.exit("picture is %d px wide, the screen is %d" % (w, SCREEN_W))

    data, stride = pack(bw, w, h)
    if len(data) > A2_FREE:
        sys.exit("%d bytes of pixels do not fit in region A2 (%d free): use a smaller --size"
                 % (len(data), A2_FREE))

    x = (SCREEN_W - w) // 2
    y = TEXT_TOP - h - LOGO_GAP

    rows = []
    for i in range(0, len(data), 16):
        rows.append("    " + ", ".join("0x%02X" % b for b in data[i:i + 16]) + ",")

    src = RUST.format(text=a.text, w=w, h=h, x=x, y=y, stride=stride, bytes=len(data),
                      free=A2_FREE, body="\n".join(rows))
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(src)

    if a.preview:
        os.makedirs(os.path.dirname(os.path.abspath(a.preview)), exist_ok=True)
        bw.convert("L").resize((w * 3, h * 3), Image.NEAREST).save(a.preview)

    print("font   : %s (%d px)" % (font_path, a.size))
    print("picture: %d x %d at (%d, %d), stride %d" % (w, h, x, y, stride))
    print("pixels : %d bytes (region A2 free %d, left %d)"
          % (len(data), A2_FREE, A2_FREE - len(data)))
    print("wrote  : %s" % a.out)
    if a.preview:
        print("preview: %s" % a.preview)


if __name__ == "__main__":
    main()
