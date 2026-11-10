#!/usr/bin/env python3
"""Recover the v0.4.0-zh10 translation dictionary from two firmware images.

Both images keep the UI text as `&str` literals in rodata, in one order. The
Chinese build has the translated literals replaced, everything else (AUTO,
DC V, CH1, SCPI keywords, ...) is byte-identical, so it anchors the alignment.

Naive "maximal printable run" extraction is useless: rustc places literals
next to each other with no separator, so dozens merge into one run. Instead
the *source* provides the dictionary: every string literal of the English
source is known, so the rodata can be tokenized by longest match. What that
tokenizer finds in both images is the untranslated part; the literals it
cannot find on the Chinese side are exactly the translated ones.

    dict  --en EN.body --zh ZH.body --src FIRMWARE/SRC --out CSV [--json J]
    runs  --zh ZH.body [--src SRC]

`unpack` the update files first (`stock/dm40fw.py unpack in.bin out.body`).
"""

import argparse
import codecs
import csv
import difflib
import io
import json
import os
import re
import sys

CJK_RANGES = (
    (0x2E80, 0x2EFF), (0x3000, 0x303F), (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0xFF00, 0xFFEF),
)


def is_cjk(ch):
    o = ord(ch)
    return any(a <= o <= b for a, b in CJK_RANGES)


def char_at(d, i):
    b = d[i]
    if 0x20 <= b <= 0x7E:
        return chr(b), 1
    if 0xC2 <= b <= 0xDF:
        n = 2
    elif 0xE0 <= b <= 0xEF:
        n = 3
    elif 0xF0 <= b <= 0xF4:
        n = 4
    else:
        return None, 0
    if i + n > len(d):
        return None, 0
    try:
        ch = codecs.decode(d[i:i + n], "utf-8")
    except UnicodeDecodeError:
        return None, 0
    if len(ch) != 1 or not is_cjk(ch):
        return None, 0
    return ch, n


# --------------------------------------------------------------- source side

LIT = re.compile(r'"((?:[^"\\\n]|\\.)*)"')


def unescape(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c != "\\":
            out.append(c)
            i += 1
            continue
        i += 1
        if i >= n:
            return None
        e = s[i]
        i += 1
        if e == "n":
            out.append("\n")
        elif e == "t":
            out.append("\t")
        elif e == "r":
            out.append("\r")
        elif e == "0":
            out.append("\0")
        elif e == "\\":
            out.append("\\")
        elif e == '"':
            out.append('"')
        elif e == "'":
            out.append("'")
        elif e == "x":
            out.append(chr(int(s[i:i + 2], 16)))
            i += 2
        elif e == "u":
            m = re.match(r"\{([0-9a-fA-F]+)\}", s[i:])
            if not m:
                return None
            out.append(chr(int(m.group(1), 16)))
            i += m.end()
        else:
            return None
    return "".join(out)


def source_literals(src):
    """Every literal worth anchoring on: ASCII, >= 3 chars, at least one letter."""
    seen = set()
    for root, _, files in os.walk(src):
        for f in files:
            if not f.endswith(".rs"):
                continue
            t = io.open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            for m in LIT.finditer(t):
                s = unescape(m.group(1))
                if not s or len(s) < 3:
                    continue
                if not all(0x20 <= ord(c) <= 0x7E for c in s):
                    continue
                if not any(c.isalpha() for c in s):
                    continue
                seen.add(s)
    return sorted(seen, key=len, reverse=True)


# ----------------------------------------------------------------- tokenizer

class Trie:
    def __init__(self, words):
        self.root = {}
        for w in words:
            node = self.root
            for b in w.encode():
                node = node.setdefault(b, {})
            node[None] = w

    def longest(self, d, i):
        node, best, j = self.root, None, i
        while j < len(d):
            node = node.get(d[j])
            if node is None:
                break
            j += 1
            if None in node:
                best = (node[None], j)
        return best


def tokenize(d, trie):
    out, i, n = [], 0, len(d)
    while i < n:
        m = trie.longest(d, i)
        if m:
            out.append((i, m[0]))
            i = m[1]
        else:
            i += 1
    return out


def cjk_spans(d, lo, hi, min_len=2, ascii_breaks=True):
    """Maximal CJK runs inside [lo, hi).

    A single CJK character decodes by chance in random bytes now and then
    (~0.15 % of positions); two in a row do not, so one-char spans are noise.

    With `ascii_breaks` an ASCII character ends the run: a translated literal
    is Chinese but neighbours may be ASCII (units, "ON", a digit), and keeping
    them would glue two literals together.
    """
    out, i = [], lo
    while i < hi:
        ch, w = char_at(d, i)
        if ch is None or (ascii_breaks and not is_cjk(ch)):
            i += 1
            continue
        start, buf = i, []
        while i < hi:
            ch, w = char_at(d, i)
            if ch is None or (ascii_breaks and not is_cjk(ch)):
                break
            buf.append(ch)
            i += w
        if len(buf) >= min_len:
            out.append((start, "".join(buf)))
    return out


def load_body(path):
    d = io.open(path, "rb").read()
    w0 = int.from_bytes(d[0:4], "little")
    w1 = int.from_bytes(d[4:8], "little")
    if not (w0 & 0x20000000) or not (0x08000000 <= w1 < 0x08100000):
        sys.exit("%s: not an unpacked body (stock/dm40fw.py unpack)" % path)
    return d


# ------------------------------------------------------------------ commands

def cmd_runs(a):
    d = load_body(a.zh)
    trie = Trie(source_literals(a.src)) if a.src else None
    print("CJK spans: %d" % len(cjk_spans(d, 0, len(d))))
    for off, s in cjk_spans(d, 0, len(d)):
        print("0x%06x  %s" % (off, s))


def cmd_dict(a):
    en, zh = load_body(a.en), load_body(a.zh)
    words = source_literals(a.src)
    trie = Trie(words)
    ten, tzh = tokenize(en, trie), tokenize(zh, trie)
    print("dictionary: %d literals" % len(words))
    print("en: %d tokens, zh: %d tokens" % (len(ten), len(tzh)))
    en_txt = [t for _, t in ten]
    zh_txt = [t for _, t in tzh]
    sm = difflib.SequenceMatcher(None, en_txt, zh_txt, autojunk=False)
    ops = sm.get_opcodes()
    print("anchor blocks: %d, matched tokens: %d"
          % (sum(1 for o in ops if o[0] == "equal"),
             sum(o[2] - o[1] for o in ops if o[0] == "equal")))
    rows, gaps = [], []
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            continue
        # English literals the Chinese build does not have as ASCII = translated
        # (or added/removed). The Chinese text sits between the neighbouring
        # anchors of the same gap.
        lo = ten[j1 - 1][0] + len(ten[j1 - 1][1]) if j1 > 0 else 0
        hi = ten[j2][0] if j2 < len(ten) else len(zh)
        if j1 >= len(tzh) and j2 == j1:
            pass
        # use the zh anchors around the gap to bound the address interval
        zlo = tzh[j1 - 1][0] + len(tzh[j1 - 1][1]) if j1 > 0 else 0
        zhi = tzh[j2][0] if j2 < len(tzh) else len(zh)
        zh_sp = [s for _, s in cjk_spans(zh, zlo, zhi)]
        en_gt = [t for t in en_txt[i1:i2]]
        if len(en_gt) == len(zh_sp):
            rows.extend(zip(en_gt, zh_sp))
        else:
            gaps.append((en_gt, zh_sp))
    uniq, seen = [], set()
    for e, z in rows:
        if (e, z) not in seen:
            seen.add((e, z))
            uniq.append((e, z, "auto"))
    for en_gt, zh_sp in gaps:
        for e in en_gt:
            uniq.append((e, "", "gap"))
        for z in zh_sp:
            uniq.append(("", z, "gap"))
    uniq.sort(key=lambda r: (r[2], r[0], r[1]))
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "zh", "status"])
        w.writerows(uniq)
    auto = sum(1 for r in uniq if r[2] == "auto")
    print("pairs: %d unique" % auto)
    print("manual queue: %d en / %d zh in %d gaps"
          % (sum(1 for r in uniq if r[2] == "gap" and r[0]),
             sum(1 for r in uniq if r[2] == "gap" and r[1]),
             len(gaps)))
    print("wrote %s" % a.out)
    if a.json:
        io.open(a.json, "w", encoding="utf-8", newline="\n").write(
            json.dumps({"pairs": uniq}, ensure_ascii=False, indent=1))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("runs")
    r.add_argument("--zh", required=True)
    r.add_argument("--src")
    d = sub.add_parser("dict")
    d.add_argument("--en", required=True)
    d.add_argument("--zh", required=True)
    d.add_argument("--src", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--json")
    a = p.parse_args()
    {"runs": cmd_runs, "dict": cmd_dict}[a.cmd](a)


if __name__ == "__main__":
    main()
