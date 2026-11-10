#!/usr/bin/env python3
"""Build patch/v041/zh_dict.csv: every UI literal of the source, with the
Chinese text the released zh10 firmware uses.

    build_dict.py --src FIRMWARE/SRC --harvest harvest.csv \
                  --zh-body zh10.body.bin --out zh_dict.csv

The three sources of a translation, in order of authority:

1. `harvest.csv` -- the pairs recorded in the v0.3.0 mkpatch scripts (this
   project's own translation memory). The wording survived into zh9/zh10, so
   these are taken as is.
2. The v0.4.0-zh10 image -- every Chinese string it contains is in its rodata.
   A harvested pair whose Chinese is *not* found there is reported as `check`:
   either the wording changed in zh9/zh10 or the string is unused now.
3. Nothing -- reported as `todo`, filled in by hand (status `manual`).
   A literal no Chinese is wanted for (SCPI keywords, DC/AC, UART/8N1, the
   12 px rows) is listed in `keep.txt` and skipped by apply_dict.py.

Comparison with the image is CJK-only on both sides: the image's spans lose
their digits and punctuation, so `5分` is matched as `分`.
"""

import argparse
import csv
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_strings import load_body, cjk_spans  # noqa: E402

LIT = re.compile(r'"((?:[^"\\\n]|\\.)*)"')
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]")


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
        simple = {"n": "\n", "t": "\t", "r": "\r", "0": "\0",
                  "\\": "\\", '"': '"', "'": "'"}
        if e in simple:
            out.append(simple[e])
        elif e == "x":
            if i + 2 > n:
                return None
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


def only_cjk(s):
    return "".join(CJK.findall(s))


def candidates(src):
    """literal -> ['file:line', ...], for the literals worth translating."""
    out = {}
    for root, _, files in os.walk(src):
        for f in sorted(files):
            if not f.endswith(".rs"):
                continue
            p = os.path.join(root, f)
            for ln, line in enumerate(io.open(p, encoding="utf-8", errors="replace"), 1):
                for m in LIT.finditer(line):
                    s = unescape(m.group(1))
                    if not s or len(s) < 2:
                        continue
                    if not all(0x20 <= ord(c) <= 0x7E for c in s):
                        continue
                    if not any(c.isalpha() for c in s):
                        continue
                    if "{" in s or "}" in s:      # formatting templates
                        continue
                    out.setdefault(s, []).append("%s:%d" % (f, ln))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--harvest", required=True)
    p.add_argument("--zh-body", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--keep", help="literals deliberately left in English")
    a = p.parse_args()

    body = load_body(a.zh_body)
    blob = "".join(s for _, s in cjk_spans(body, 0, len(body)))
    keep = set()
    if a.keep and os.path.exists(a.keep):
        keep = set(l.strip() for l in io.open(a.keep, encoding="utf-8") if l.strip()
                   and not l.startswith("#"))

    harvest = {}
    for row in csv.DictReader(io.open(a.harvest, encoding="utf-8")):
        harvest[row["en"]] = row["zh"]

    lit = candidates(a.src)
    rows, counts = [], {"auto": 0, "check": 0, "todo": 0, "keep": 0}
    for en in sorted(lit):
        where = ",".join(lit[en][:4])
        if en in keep:
            rows.append((en, "", "keep", where))
            counts["keep"] += 1
            continue
        zh = harvest.get(en)
        if not zh:
            rows.append((en, "", "todo", where))
            counts["todo"] += 1
            continue
        norm = only_cjk(zh)
        if norm and norm in blob:
            rows.append((en, zh, "auto", where))
            counts["auto"] += 1
        else:
            rows.append((en, zh, "check", where))
            counts["check"] += 1
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "zh", "status", "where"])
        w.writerows(rows)
    print("literals: %d" % len(lit))
    print(" ".join("%s=%d" % (k, v) for k, v in counts.items()))
    print("wrote %s" % a.out)


main()
