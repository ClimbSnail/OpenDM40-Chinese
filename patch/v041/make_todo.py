#!/usr/bin/env python3
"""Assemble the translation scope and todo list for v0.4.1.

Scope, not "every literal in the tree" (2,000+ of those are SCPI tables, log
formats and unit strings that stay English):

  * the pairs harvested from the v0.3.0 mkpatch scripts, where the English
    still exists in v0.4.1 -- this project's own translation memory;
  * the literals the image alignment proved were translated in zh10
    (`left.csv`: the English strings missing from the Chinese image);
  * the literals v0.4.1 added over v0.4.0 (the low-battery dialogs, the new
    DMM sub-mode label).

    make_todo.py --src FIRMWARE/SRC --src-old V040/SRC --harvest harvest.csv \
                 --left left.csv --dict zh_dict.csv --out todo.csv
"""

import argparse
import csv
import io
import os
import re

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
        simple = {"n": "\n", "t": "\t", "r": "\r", "0": "\0",
                  "\\": "\\", '"': '"', "'": "'"}
        if e in simple:
            out.append(simple[e])
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


def literals(root):
    out = {}
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if not f.endswith(".rs"):
                continue
            p = os.path.join(dirpath, f)
            for ln, line in enumerate(io.open(p, encoding="utf-8", errors="replace"), 1):
                for m in LIT.finditer(line):
                    s = unescape(m.group(1))
                    if not s or len(s) < 2:
                        continue
                    if not all(0x20 <= ord(c) <= 0x7E for c in s):
                        continue
                    if not any(c.isalpha() for c in s):
                        continue
                    if "{" in s or "}" in s:
                        continue
                    out.setdefault(s, []).append("%s:%d" % (f, ln))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--src-old", required=True)
    p.add_argument("--harvest", required=True)
    p.add_argument("--left", required=True)
    p.add_argument("--dict", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()

    now, old = literals(a.src), literals(a.src_old)
    harvest = {}
    for r in csv.DictReader(io.open(a.harvest, encoding="utf-8")):
        harvest[r["en"]] = r["zh"]
    left = [r["en"] for r in csv.DictReader(io.open(a.left, encoding="utf-8"))]

    rows = {}

    def add(en, zh, status):
        rows[en] = [en, zh, status, ",".join(now.get(en, [])[:4])]

    for en, zh in harvest.items():
        if en in now:
            add(en, zh, "harvest")
    for en in left:
        if en in now and en not in rows:
            add(en, "", "todo")
    for en in now:
        if en not in old and len(en) >= 3 and en not in rows:
            add(en, "", "new")

    out = sorted(rows.values(), key=lambda r: (r[1] != "", r[0]))
    with io.open(a.dict, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "zh", "status", "where"])
        w.writerows(out)
    need = [r for r in out if not r[1]]
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f)
        w.writerow(["en", "status", "where"])
        w.writerows([[r[0], r[2], r[3]] for r in need])
    print("scope %d: harvest %d, todo %d, new %d"
          % (len(out), sum(1 for r in out if r[1]),
             sum(1 for r in need if r[2] == "todo"),
             sum(1 for r in need if r[2] == "new")))


if __name__ == "__main__":
    main()
