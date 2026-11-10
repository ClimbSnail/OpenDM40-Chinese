#!/usr/bin/env python3
"""Set the vendor line of the device info page.

The page's rows are an array in `app.rs`; the dictionary turns upstream's
`("Vendor", "Alientek")` into `("厂商", "正点原子")`, and this script appends
the project's own mark to the value. It is not a translation, so it does not
belong in `zh_dict.csv`: the dictionary stays "upstream English -> Chinese",
and anything this fork adds on top lives in its own script like this one.

    vendor_name.py --src firmware/src [--value "正点原子 & 蜗牛"]

Idempotent: a tree that already shows the new value is left alone. Whatever
value an earlier run left behind is replaced, so changing the mark only means
re-running this with another --value.
"""

import argparse
import io
import os
import re
import sys

# The row, whatever value it currently carries. `厂商` is unique on the page,
# so the match count must be exactly one.
ROW = re.compile(r'\("厂商", "[^"\n]*"\),')


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--value", default="正点原子 & 蜗牛")
    a = p.parse_args()

    path = os.path.join(a.src, "app.rs")
    text = io.open(path, encoding="utf-8").read()
    new = '("厂商", "%s"),' % a.value

    if new in text:
        print("app.rs: vendor already %s" % a.value)
        return

    hits = ROW.findall(text)
    if len(hits) != 1:
        sys.exit("app.rs: expected 1 vendor row, found %d -- upstream or the "
                 "dictionary changed, fix the anchor" % len(hits))

    io.open(path, "w", encoding="utf-8", newline="\n").write(ROW.sub(lambda _: new, text))
    print("app.rs: vendor %s -> %s" % (hits[0], new))


if __name__ == "__main__":
    main()
