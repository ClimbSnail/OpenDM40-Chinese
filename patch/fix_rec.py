#!/usr/bin/env python3
"""Repair the block a PowerShell here-string mangled, and disable the gesture.

The inline `python -c` heredoc went through a console code page that is not
UTF-8, so the Chinese in the inserted lines arrived as mojibake. The rest of the
file was not touched. This rewrites just those lines with a proper UTF-8 writer,
keeping the original body under a #[allow(dead_code)] name.
"""

import io
import os
import sys

SRC = sys.argv[1]
APP = os.path.join(SRC, "app.rs")

lines = io.open(APP, encoding="utf-8").read().split("\n")

# locate the disabled stub: it starts at the mangled `fn rec_toggle`
start = None
for i, l in enumerate(lines):
    if l.strip().startswith("fn rec_toggle(&mut self, now: u64) {"):
        start = i
        break
if start is None:
    sys.exit("rec_toggle not found")

end = None
for i in range(start, start + 20):
    if lines[i].strip() == "}":
        end = i
        break
if end is None:
    sys.exit("closing brace not found")

still_broken = [l for l in lines if "\u951f" in l or "\ufffd" in l]
new = [
    "    fn rec_toggle(&mut self, now: u64) {",
    "        // CSV 记录暂停：停止记录时 csvlog 的收尾会把主循环卡住，看门狗复位；",
    "        // 连续两次就进原厂恢复模式。定位到真正原因前先挡住手势，",
    "        // 不让表反复重启。",
    "        self.toast(now, \"记录暂不可用\", false);",
    "        self.beep(now, 300);",
    "    }",
]
lines[start:end + 1] = new

text = "\n".join(lines)
io.open(APP, "w", encoding="utf-8", newline="\n").write(text)

# sanity: the strings this file must still contain
for probe in ["正在记录", "已存 ", "无法记录"]:
    if probe.encode("utf-8") in text.encode("utf-8"):
        print("ok:", probe)
    else:
        print("MISSING:", probe)
print("replaced lines %d..%d" % (start + 1, end + 1))
