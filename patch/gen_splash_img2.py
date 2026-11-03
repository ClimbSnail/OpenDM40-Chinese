"""生成开机画面位图（200x55 单色，放 A2；已按 A2 余量 1414 字节选定）。"""

import io
import os

from PIL import Image

SRC = r"F:\desk\study\DM40A\loge\xingyan_1.jpg"
OUT = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src\splash_img.rs"

BOX = (128, 120, 352, 182)      # 224 x 62 原文
W, H = 200, 55                  # 缩到这尺寸
THR = 140
TOP = 110                       # 图片顶端 y

im = Image.open(SRC).convert("L").crop(BOX).resize((W, H), Image.LANCZOS)
bw = im.point(lambda p: 255 if p > THR else 0).convert("1")

stride = (W + 7) // 8
data = bytearray()
for y in range(H):
    for bx in range(stride):
        byte = 0
        for bit in range(8):
            x = bx * 8 + bit
            if x < W and bw.getpixel((x, y)):
                byte |= 0x80 >> bit
        data.append(byte)
assert len(data) == stride * H

rows = []
for i in range(0, len(data), 16):
    rows.append("    " + ", ".join("0x%02X" % b for b in data[i:i + 16]) + ",")
body = "\n".join(rows)

RUST = '''//! Boot splash picture: the "xingyan" wordmark, %d x %d, 1 bpp (MSB first,
//! %d bytes per row, no padding). %d bytes of pixels.
//!
//! The bitmap lives in **region A2** (`.rodata.a2.splash`, zero-wait flash,
//! ~1.4 KB free); the blit loop is ordinary code in region B. Drawn once by
//! `native::splash::draw`; nothing here runs after boot.

use crate::lcd;
use crate::ui::{BG, FG};

/// Picture width and height in pixels, and its top-left corner.
pub const W: i16 = %d;
pub const H: i16 = %d;
pub const X: i16 = %d;
pub const Y: i16 = %d;

#[link_section = ".rodata.a2.splash"]
static IMG: [u8; %d] = [
%s
];

/// Paint the picture: clear its box, then one `fill_rect` per run of set
/// bits (a few hundred calls, well under a millisecond).
pub fn draw() {
    lcd::fill_rect(X as u16, Y as u16, W as u16, H as u16, BG);
    let stride = (W as usize + 7) / 8;
    for row in 0..H as usize {
        let base = row * stride;
        let mut x = 0usize;
        while x < W as usize {
            if IMG[base + x / 8] & (0x80 >> (x %% 8)) == 0 {
                x += 1;
                continue;
            }
            let start = x;
            while x < W as usize && IMG[base + x / 8] & (0x80 >> (x %% 8)) != 0 {
                x += 1;
            }
            let (px, py) = ((X as usize + start) as u16, (Y as usize + row) as u16);
            lcd::fill_rect(px, py, (x - start) as u16, 1, FG);
        }
    }
}
''' % (W, H, stride, len(data), W, H, (480 - W) // 2, TOP, len(data), body)

io.open(OUT, "w", encoding="utf-8", newline="\n").write(RUST)
print("已生成 %s（%d 字节位图，A2 余量 %d）" % (OUT, len(data), 1414 - len(data)))
