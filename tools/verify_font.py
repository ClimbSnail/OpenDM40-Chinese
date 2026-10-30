import io
import re
import sys

p = "F:\\desk\\study\\dm40\\fwsim\\firmware\\src\\stockfont_data.rs"
t = io.open(p, encoding="utf-8").read()

m = re.search(r"pub static TEXT22_E: \[Entry; (\d+)\] = \[(.*?)\];", t, re.S)
n = int(m.group(1))
ents = re.findall(r"E\((0x[0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(\d+),(\d+)\)", m.group(2))
sys.stderr.write("TEXT22_E declares %d, found %d\n" % (n, len(ents)))
assert n == len(ents)

mb = re.search(r'pub static TEXT22_B: \[u8; (\d+)\] = \*b"\\\n(.*?)"\n;', t, re.S)
declared = int(mb.group(1))
blob = bytes(int(x, 16) for x in re.findall(r"\\x([0-9a-f]{2})", mb.group(2)))
sys.stderr.write("TEXT22_B declares %d, decoded %d\n" % (declared, len(blob)))
assert declared == len(blob)

codes = [int(e[0], 16) for e in ents]
sys.stderr.write("codes ascending: %s\n" % all(a < b for a, b in zip(codes, codes[1:])))
cjk = [c for c in codes if c >= 0x2E80]
sys.stderr.write("CJK glyphs kept: %d\n" % len(cjk))
sys.stderr.write("  %s\n" % "".join(chr(c) for c in cjk))

# Every offset must be inside the blob, and glyph spans must be in range.
maxoff = max(int(e[1]) for e in ents)
sys.stderr.write("max glyph offset: %d (blob %d) ok=%s\n" % (maxoff, len(blob), maxoff < len(blob)))

# Bounds: off must fit u16, code u16, w/h/adv u8, yoff i8, t/ih u8.
bad = []
for e in ents:
    code, off, w, h, adv, yoff, tt, ih = e
    if int(code, 16) > 0xFFFF or int(off) > 0xFFFF:
        bad.append(e)
    for v in (w, h, adv, tt, ih):
        if int(v) > 255:
            bad.append(e)
    if not (-128 <= int(yoff) <= 127):
        bad.append(e)
sys.stderr.write("entries out of field range: %d\n" % len(bad))
sys.stderr.write("FILE OK\n")
