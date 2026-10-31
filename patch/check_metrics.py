#!/usr/bin/env python3
"""Check that every TEXT22 glyph has the same vertical metrics.

The font mixes two sources: 94 glyphs copied from the vendor's DM40 V2.6 font
and 144 drawn from SimSun. If the drawn ones do not land on the same ink rows
they look smaller or sit higher than their neighbours -- which is exactly the
bug the user reported earlier.

For TEXT22 the encoding is: h = cell height (always 22), t = the ink's first
row, ih = ink height, yoff = 0. The vendor hanzi are t=1..2, ih=19..20.
"""

import io
import re
import sys
from collections import Counter

p = sys.argv[1]
t = io.open(p, encoding="utf-8").read()

m = re.search(r"pub static TEXT22_E: \[Entry; (\d+)\] = \[(.*?)\];", t, re.S)
ents = [(int(a, 16), int(b), int(c), int(d), int(e), int(f), int(g), int(h))
        for a, b, c, d, e, f, g, h in
        re.findall(r"E\((0x[0-9A-Fa-f]+),(\d+),(\d+),(\d+),(\d+),(-?\d+),(\d+),(\d+)\)", m.group(2))]

cjk = [e for e in ents if e[0] >= 0x2E80]
lat = [e for e in ents if 0x20 <= e[0] < 0x7F]
other = [e for e in ents if e not in cjk and e not in lat]

print("TEXT22 glyphs: %d  (CJK %d, ASCII %d, other %d)" % (len(ents), len(cjk), len(lat), len(other)))
print()

def report(name, group):
    if not group:
        return
    print("%s" % name)
    print("   h   (cell)  :", dict(Counter(e[3] for e in group)))
    print("   t   (ink top):", dict(Counter(e[6] for e in group)))
    print("   ih  (ink h)  :", dict(Counter(e[7] for e in group)))
    print("   ink rows     : %d..%d" % (min(e[6] for e in group), max(e[6] + e[7] - 1 for e in group)))
    print("   adv         :", dict(Counter(e[4] for e in group)))
    print()

report("CJK (hanzi)", cjk)
report("ASCII (latin)", lat)

# 一致性判定：CJK 的 h 必须都是 22，adv 都是 22，yoff 都是 0
bad_h = [e for e in cjk if e[3] != 22]
bad_adv = [e for e in cjk if e[4] != 22]
bad_yoff = [e for e in cjk if e[5] != 0]
print("CJK with h != 22 :", len(bad_h))
print("CJK with adv != 22:", len(bad_adv))
print("CJK with yoff != 0:", len(bad_yoff))

# 墨迹顶端不一致的字
tops = Counter(e[6] for e in cjk)
print("CJK ink-top spread:", dict(tops))
ihs = Counter(e[7] for e in cjk)
print("CJK ink-height spread:", dict(ihs))
if len(tops) > 2 or (max(ihs) - min(ihs)) > 2:
    print("\n!! 不一致：墨迹顶端或高度分布过宽")
else:
    print("\nOK: 汉字墨迹统一在 %d..%d 行，高 %d..%d 行"
          % (min(tops), max(tops), min(ihs), max(ihs)))
