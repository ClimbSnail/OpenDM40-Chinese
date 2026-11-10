#!/usr/bin/env python3
"""Merge the scope list, the harvested pairs and the hand translations, then
check every Chinese string against the released zh10 image.

    merge_dict.py --dict zh_dict.csv --manual zh_manual.tsv \
                  --zh-body zh10.body.bin --out zh_dict.csv [--misses miss.csv]

The check is CJK-only on both sides (the image's spans lose digits and
punctuation), so a `miss` means the wording differs from zh10 -- either the
translation is mine rather than the project's, or the string is new in v0.4.1.
Those rows are listed for review; they do not stop the build.
"""

import argparse
import csv
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_strings import cjk_spans, load_body  # noqa: E402

# Ideographs only: the image's spans do not keep the full-width colon or the
# brackets (they are separate bytes there), and a label's "：" must not make
# the whole string unmatched.
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dict", required=True)
    p.add_argument("--manual", required=True)
    p.add_argument("--zh-body", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--misses")
    a = p.parse_args()

    manual = {}
    for line in io.open(a.manual, encoding="utf-8"):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            sys.exit("bad row: %r" % line)
        manual[parts[0].strip()] = (parts[1].strip(), parts[2].strip())

    body = load_body(a.zh_body)
    # Same normalisation on both sides: ideographs only.
    blob = "".join(CJK.findall("".join(s for _, s in cjk_spans(body, 0, len(body)))))

    rows, misses = [], []
    for r in csv.DictReader(io.open(a.dict, encoding="utf-8")):
        en, zh, status = r["en"], r["zh"], r["status"]
        # `zh_manual.tsv` is the reviewed list: it also overrides a harvested
        # pair whose wording zh10 no longer uses.
        key = en if en in manual else en.strip()
        if key in manual:
            mzh, kind = manual[key]
            if kind == "keep":
                zh, status = "", "keep"
            else:
                zh, status = mzh, ("manual" if status in ("todo", "harvest") else "manual-new")
        if zh:
            norm = "".join(CJK.findall(zh))
            if norm and norm not in blob:
                misses.append((en, zh, status))
        rows.append((en, zh, status, r["where"]))

    with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "zh", "status", "where"])
        w.writerows(rows)
    if a.misses:
        with io.open(a.misses, "w", encoding="utf-8", newline="\n") as f:
            w = csv.writer(f)
            w.writerow(["en", "zh", "status"])
            w.writerows(misses)
    todo = [r for r in rows if not r[1]]
    print("rows %d: translated %d, keep %d, still empty %d"
          % (len(rows), sum(1 for r in rows if r[1] and r[2] != "keep"),
             sum(1 for r in rows if r[2] == "keep"), len(todo)))
    print("not found in zh10 (review): %d" % len(misses))
    for en, zh, st in misses[:40]:
        print("   %-40s %-16s %s" % (en[:40], zh, st))
    if todo:
        print("missing translations:")
        for r in todo:
            print("   %s" % r[0])


if __name__ == "__main__":
    main()
