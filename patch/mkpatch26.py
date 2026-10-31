#!/usr/bin/env python3
"""The screenshot / recording toasts: the green one a gesture pops up.

    *b"Saved S000.BMP"    -> 已存 S001.BMP
    *b"Saved LOG000.DLG"  -> 已存 LOG001.DLG

The file name stays ASCII (it is the real name on the disk), only the verb
changes. These strings are assembled in a fixed byte buffer, so the buffer grows
from 13 to 24 bytes and the digit offsets move with the prefix length.

The failure toasts are here too: No disk / Disk full / Disk busy /
Screenshot failed / Log failed / Disk full: log ended.

    python mkpatch26.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
APP = os.path.join(SRC, "app.rs")

app = io.open(APP, encoding="utf-8").read()


def sub(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit("%s: %d matches" % (label, n))
    return text.replace(old, new)


# ---- recording -------------------------------------------------------
app = sub(app,
          '        let mut t = *b"Saved LOG000.DLG";\n'
          '        let (txt, ok) = match (st.state, st.file) {\n'
          '            (State::Done, Some(n)) => {\n'
          '                t[9] = b\'0\' + (n / 100 % 10) as u8;\n'
          '                t[10] = b\'0\' + (n / 10 % 10) as u8;\n'
          '                t[11] = b\'0\' + (n % 10) as u8;\n'
          '                (core::str::from_utf8(&t).unwrap_or("Saved"), true)\n'
          '            }\n'
          '            (State::Full, _) => ("Disk full: log ended", false),\n'
          '            (State::NoDisk, _) => ("No disk", false),\n'
          '            _ => ("Log failed", false),\n'
          '        };',
          '        // "已存 " + "LOG000.DLG": the file name stays ASCII, the verb does not.\n'
          '        let pre = "已存 ";\n'
          '        let mut t = [0u8; 24];\n'
          '        let (txt, ok) = match (st.state, st.file) {\n'
          '            (State::Done, Some(n)) => {\n'
          '                t[..pre.len()].copy_from_slice(pre.as_bytes());\n'
          '                t[pre.len()..pre.len() + 11].copy_from_slice(b"LOG000.DLG");\n'
          '                let k = pre.len();\n'
          '                t[k + 3] = b\'0\' + (n / 100 % 10) as u8;\n'
          '                t[k + 4] = b\'0\' + (n / 10 % 10) as u8;\n'
          '                t[k + 5] = b\'0\' + (n % 10) as u8;\n'
          '                (core::str::from_utf8(&t[..k + 11]).unwrap_or("已存"), true)\n'
          '            }\n'
          '            (State::Full, _) => ("磁盘已满, 记录结束", false),\n'
          '            (State::NoDisk, _) => ("无磁盘", false),\n'
          '            _ => ("记录失败", false),\n'
          '        };',
          "rec_toast")

# ---- screenshot ------------------------------------------------------
app = sub(app,
          '        let mut t = *b"Saved S000.BMP";\n'
          '        let (txt, ok) = match shot {\n'
          '            Shot::Saved(n) => {\n'
          '                t[7] = b\'0\' + (n / 100 % 10) as u8;\n'
          '                t[8] = b\'0\' + (n / 10 % 10) as u8;\n'
          '                t[9] = b\'0\' + (n % 10) as u8;\n'
          '                (core::str::from_utf8(&t).unwrap_or("Saved"), true)\n'
          '            }\n'
          '            Shot::NoDisk => ("No disk", false),\n'
          '            Shot::Full => ("Disk full", false),\n'
          '            Shot::Error => ("Screenshot failed", false),\n'
          '            Shot::Busy => ("Disk busy", false),\n'
          '        };',
          '        // "已存 " + "S000.BMP" (the name the meter writes stays ASCII).\n'
          '        let pre = "已存 ";\n'
          '        let mut t = [0u8; 24];\n'
          '        let (txt, ok) = match shot {\n'
          '            Shot::Saved(n) => {\n'
          '                t[..pre.len()].copy_from_slice(pre.as_bytes());\n'
          '                t[pre.len()..pre.len() + 8].copy_from_slice(b"S000.BMP");\n'
          '                let k = pre.len();\n'
          '                t[k + 1] = b\'0\' + (n / 100 % 10) as u8;\n'
          '                t[k + 2] = b\'0\' + (n / 10 % 10) as u8;\n'
          '                t[k + 3] = b\'0\' + (n % 10) as u8;\n'
          '                (core::str::from_utf8(&t[..k + 8]).unwrap_or("已存"), true)\n'
          '            }\n'
          '            Shot::NoDisk => ("无磁盘", false),\n'
          '            Shot::Full => ("磁盘已满", false),\n'
          '            Shot::Error => ("截图失败", false),\n'
          '            Shot::Busy => ("磁盘忙", false),\n'
          '        };',
          "shot_toast")

io.open(APP, "w", encoding="utf-8", newline="\n").write(app)
sys.stderr.write("done: screenshot + recording toasts in Chinese\n")
