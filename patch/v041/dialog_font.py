#!/usr/bin/env python3
"""Draw the translated dialog / toast text with a face that has hanzi.

`dialog.rs` draws every overlay through `centred_sp`, and it hard-coded the
stock 26 px ASCII font (`sf::ASCII26`). That face is the vendor's ASCII table
and stops at '~': the hanzi this project translated into those strings had no
glyph, so the firmware-download question (`固件已接收 / 现在安装？`), the
power-off confirm, the logger panel title and every Chinese toast came out as
an empty box with two empty buttons -- and the build said nothing, because the
literals are valid UTF-8 and the font is a valid font.

`check_fonts.py` missed it for the same reason: the literal and the font name
are on different lines (the font sits inside the helper), so the line-based
heuristic saw a CJK literal with no font on the line and skipped it.

The fix keeps the stock look for ASCII text (it *is* the larger face the
vendor drew these dialogs in) and switches to TEXT22 -- the only face with
hanzi -- as soon as the string holds anything else. The face is chosen at the
draw site, so no caller has to care.

    dialog_font.py --src firmware/src

Idempotent: a tree that already picks the face by content is left alone.
"""

import argparse
import io
import os
import sys

DIALOG_OLD = """fn centred_sp(r: (u16, u16, u16, u16), s: &str, fg: Color, bg: Color, spacing: i8) {
    sf::label(sf::ASCII26, rect(r.0 as i16, r.1 as i16, r.2 as i16, r.3 as i16), s, fg, bg, 8, spacing);
}
"""

DIALOG_NEW = """/// The face a label needs: the stock 26 px ASCII font for ASCII text (it is
/// the larger one the vendor drew these overlays in), TEXT22 as soon as the
/// string holds anything else. ASCII26's table stops at '~', so a translated
/// label through it is blank on the panel and the build says nothing.
pub fn face(s: &str) -> sf::Font {
    if s.is_ascii() { sf::ASCII26 } else { sf::TEXT22 }
}

fn centred_sp(r: (u16, u16, u16, u16), s: &str, fg: Color, bg: Color, spacing: i8) {
    sf::label(face(s), rect(r.0 as i16, r.1 as i16, r.2 as i16, r.3 as i16), s, fg, bg, 8, spacing);
}
"""

# The gallery's delete / rename confirm draws its own box with the same font
# and the same Chinese buttons ("取消" / "确定").
GALLERY_OLD = ("    let lab = |r: (u16, u16, u16, u16), s: &str, bg: Color| "
               "sf::label(sf::ASCII26, r4(r), s, D_FG, bg, 8, 1);\n")
GALLERY_NEW = ("    let lab = |r: (u16, u16, u16, u16), s: &str, bg: Color| "
               "sf::label(crate::dialog::face(s), r4(r), s, D_FG, bg, 8, 1);\n")


def patch(path, old, new, done):
    text = io.open(path, encoding="utf-8").read()
    if done in text:
        print("%s: already patched" % os.path.basename(path))
        return
    n = text.count(old)
    if n != 1:
        sys.exit("%s: expected 1 hit, found %d -- upstream changed, fix the anchor"
                 % (os.path.basename(path), n))
    io.open(path, "w", encoding="utf-8", newline="\n").write(text.replace(old, new))
    print("%s: label face now picked by content" % os.path.basename(path))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    a = p.parse_args()

    patch(os.path.join(a.src, "dialog.rs"), DIALOG_OLD, DIALOG_NEW, "pub fn face(s: &str) -> sf::Font")
    patch(os.path.join(a.src, "gallery.rs"), GALLERY_OLD, GALLERY_NEW, "crate::dialog::face(s)")


if __name__ == "__main__":
    main()
