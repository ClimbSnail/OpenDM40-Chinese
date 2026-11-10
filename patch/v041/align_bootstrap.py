#!/usr/bin/env python3
"""Align the English and Chinese v0.4.0 images to build the translation memory.

Both images hold the same literals in (almost) the same order; the ASCII ones
are byte-identical, which gives ~1,000 anchors. What is left between two
anchors is, on the English side, the literals that got translated and, on the
Chinese side, the Chinese text -- except that rustc packs adjacent literals
with no separator, so several Chinese strings arrive as one span.

So the pairing is bootstrapped:

  pass 1   split every Chinese span with the dictionary we already have (the
           184 pairs harvested from the v0.3.0 mkpatch scripts)
  pass k   the gaps whose English and Chinese counts now agree are paired and
           their Chinese strings join the dictionary, which splits more spans
           in pass k+1

Stops when no new pair appears. Whatever remains is written to a manual queue,
to be filled in by hand -- it is small once the dictionary covers the common
short strings (确定 / 取消 / 返回 / 设置 ...).

    align_bootstrap.py --en EN.body --zh ZH.body --src SRC --harvest CSV \
                       --out-dict dict.csv --out-left left.csv
"""

import argparse
import csv
import difflib
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_strings import (  # noqa: E402
    Trie, cjk_spans, is_cjk, load_body, source_literals, tokenize)

MAX_GAP = 64


def split_with(dict_trie, span, min_known=2):
    """Cut the known strings out of a span; unknown runs stay whole.

    Letting unknown characters fall back to one piece each would inflate the
    count and no gap could ever match, so they are accumulated and emitted as
    they are. A known string of a single character is not cut out either: it
    appears inside longer words too often (开 in 开始记录).
    """
    b = span.encode()
    out, cur, i = [], b"", 0
    while i < len(b):
        m = dict_trie.longest(b, i)
        if m and len(m[0]) >= min_known:
            if cur:
                out.append(cur.decode("utf-8", "replace"))
                cur = b""
            out.append(m[0])
            i = m[1]
            continue
        n = 1 if b[i] < 0x80 else (3 if b[i] >= 0xE0 else 2)
        cur += b[i:i + n]
        i += n
    if cur:
        out.append(cur.decode("utf-8", "replace"))
    return out


def gaps(en_tok, zh_tok):
    """[(en_lits, zh_tokens_before, zh_tokens_after)] for the unmatched runs."""
    sm = difflib.SequenceMatcher(None, [t for _, t in en_tok], [t for _, t in zh_tok],
                                 autojunk=False)
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        out.append((en_tok[i1:i2], j1, j2))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--en", required=True)
    p.add_argument("--zh", required=True)
    p.add_argument("--src", required=True)
    p.add_argument("--harvest", required=True)
    p.add_argument("--out-dict", required=True)
    p.add_argument("--out-left", required=True)
    a = p.parse_args()

    en, zh = load_body(a.en), load_body(a.zh)
    trie = Trie(source_literals(a.src))
    ten, tzh = tokenize(en, trie), tokenize(zh, trie)
    zsp = cjk_spans(zh, 0, len(zh), min_len=2)
    print("en tokens %d, zh tokens %d, zh spans %d" % (len(ten), len(tzh), len(zsp)))

    done = {}
    for row in csv.DictReader(io.open(a.harvest, encoding="utf-8")):
        done[row["en"]] = row["zh"]
    seeded = set(done)
    seed = len(done)

    for it in range(12):
        dtrie = Trie([v for v in done.values() if len(v) >= 1])
        added = 0
        for en_lits, j1, j2 in gaps(ten, tzh):
            lo = tzh[j1 - 1][0] + len(tzh[j1 - 1][1]) if j1 > 0 else 0
            hi = tzh[j2][0] if j2 < len(tzh) else len(zh)
            spans = [s for o, s in zsp if lo <= o < hi]
            pieces = []
            for s in spans:
                pieces.extend(split_with(dtrie, s))
            lits = [t for _, t in en_lits if len(t) >= 2]
            if not lits or len(lits) != len(pieces):
                continue
            if len(lits) > MAX_GAP:
                continue
            for e, z in zip(lits, pieces):
                if e in done:
                    continue
                if not z or not is_cjk(z[0]):
                    continue
                done[e] = z
                added += 1
        print("pass %d: +%d pairs (total %d)" % (it + 1, added, len(done)))
        if added == 0:
            break

    # what is left: English literals seen in the image but still untranslated
    left = []
    for en_lits, j1, j2 in gaps(ten, tzh):
        for _, t in en_lits:
            if t not in done:
                left.append(t)
    left = sorted(set(left))
    with io.open(a.out_dict, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "zh", "src"])
        for e in sorted(done):
            w.writerow([e, done[e], "harvest" if e in seeded else "align"])
    with io.open(a.out_left, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en"])
        for t in left:
            w.writerow([t])
    print("seeded %d, aligned %d, left %d" % (seed, len(done) - seed, len(left)))
    print("wrote %s, %s" % (a.out_dict, a.out_left))


if __name__ == "__main__":
    main()
