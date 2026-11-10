#!/usr/bin/env python3
"""Harvest the English -> Chinese pairs recorded in the v0.3.0 mkpatch scripts.

Those scripts are archived in `patch/legacy-v030/` -- `--patch-dir` points
there now (`patch/mkpatch*.py` before the 2026-11-10 tidy-up). `mkpatch*.py`
and the one-off fix scripts are text replacements of the
form

    (OLD_CODE, NEW_CODE)

where both sides are Rust source snippets: the English literals in OLD_CODE
became the Chinese ones in NEW_CODE, in the same order. Those pairs are the
project's own translation memory for v0.3.0 -- the wording carried over into
zh9/zh10 almost unchanged -- so they seed the v0.4.1 dictionary instead of
translating 400 strings from scratch again.

    harvest.py --patch-dir PATCH --out CSV

A pair is only taken when both snippets yield the same number of literals
(otherwise the edit also added or removed strings, and the pairing would be a
guess). Multi-line snippets are handled; `\\n`, `\\u{...}` and `\\xNN` are
decoded.
"""

import argparse
import ast
import codecs
import csv
import io
import os
import re
import sys

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


def literals(code):
    out = []
    for m in LIT.finditer(code):
        s = unescape(m.group(1))
        if s is None:
            return []
        out.append(s)
    return out


def pairs_from(code_old, code_new):
    a, b = literals(code_old), literals(code_new)
    if not a or len(a) != len(b):
        return []
    out = []
    for x, y in zip(a, b):
        if x == y:
            continue
        if not any(c.isalpha() for c in x):
            continue
        if not any(0x4E00 <= ord(c) <= 0x9FFF for c in y):
            continue
        out.append((x, y))
    return out


def walk(node, found):
    if isinstance(node, ast.Tuple) and len(node.elts) == 2:
        vals = []
        for e in node.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                vals.append(e.value)
        if len(vals) == 2:
            found.extend(pairs_from(vals[0], vals[1]))
            return
    for child in ast.iter_child_nodes(node):
        walk(child, found)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--patch-dir", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    found = []
    files = 0
    for f in sorted(os.listdir(a.patch_dir)):
        if not f.endswith(".py") or f == os.path.basename(__file__):
            continue
        path = os.path.join(a.patch_dir, f)
        try:
            tree = ast.parse(io.open(path, encoding="utf-8").read())
        except SyntaxError:
            continue
        files += 1
        walk(tree, found)
    uniq, seen = [], set()
    for en, zh in found:
        if en in seen:
            continue
        seen.add(en)
        uniq.append((en, zh))
    uniq.sort()
    with io.open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        w = csv.writer(fh)
        w.writerow(["en", "zh", "src"])
        for en, zh in uniq:
            w.writerow([en, zh, "mkpatch"])
    print("%d scripts, %d pairs (%d unique)" % (files, len(found), len(uniq)))
    print("wrote %s" % a.out)


main()
