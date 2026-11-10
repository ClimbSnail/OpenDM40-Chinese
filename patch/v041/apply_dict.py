#!/usr/bin/env python3
"""Replace the UI literals of the v0.4.1 source with the reviewed Chinese.

    apply_dict.py --dict zh_dict.csv --src FIRMWARE/SRC [--log apply.log]

Only whole string literals are touched: a literal is decoded, looked up in
the dictionary, and the *raw* text inside the quotes is replaced. Nothing is
substring-matched, so `"Settings > More"` cannot turn into `"设置 > 更多 >"`.

Byte strings (`b"..."`) and raw strings are left alone, and so is every
literal whose status is `keep` (SCPI keywords, DC/AC, UART/8N1, the 12 px
rows) -- those stay English on purpose.

Every dictionary row must be used at least once, otherwise the run fails:
that catches a row whose English no longer exists upstream (a renamed
literal), which would silently drop a translation.
"""

import argparse
import io
import os
import re
import sys

LIT = re.compile(r'(?<![A-Za-z0-9_])"((?:[^"\\\n]|\\.)*)"')


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


def escape(s):
    """Rust literal body for `s`: UTF-8 as is, quotes and backslashes escaped."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dict", required=True)
    p.add_argument("--src", required=True)
    p.add_argument("--log")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    import csv
    table = {}
    for r in csv.DictReader(io.open(a.dict, encoding="utf-8")):
        if r["status"] == "keep" or not r["zh"]:
            continue
        table[r["en"]] = r["zh"]

    used = {}
    rows = []
    for dirpath, _, files in os.walk(a.src):
        for f in sorted(files):
            if not f.endswith(".rs"):
                continue
            path = os.path.join(dirpath, f)
            text = io.open(path, encoding="utf-8").read()

            def sub(m):
                raw = m.group(1)
                dec = unescape(raw)
                if dec is None or dec not in table:
                    return m.group(0)
                zh = table[dec]
                used.setdefault(dec, 0)
                used[dec] += 1
                rows.append((f, dec, zh, used[dec]))
                return '"%s"' % escape(zh)

            new = LIT.sub(sub, text)
            if new != text and not a.dry_run:
                io.open(path, "w", encoding="utf-8", newline="\n").write(new)

    unused = sorted(set(table) - set(used))
    if a.log:
        with io.open(a.log, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("file\ten\tzh\thit\n")
            for f, en, zh, n in sorted(rows):
                fh.write("%s\t%s\t%s\t%d\n" % (f, en, zh, n))
    print("replaced %d literals (%d distinct)" % (len(rows), len(used)))
    if unused:
        print("NOT FOUND in the source (%d):" % len(unused))
        for en in unused:
            print("   %s" % en)
        if not a.dry_run:
            sys.exit(1)


if __name__ == "__main__":
    main()
