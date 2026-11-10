#!/usr/bin/env python3
"""Undo the diagnostic freeze: back to the shipping panic handler.

Keeps the buzzer silence and the magenta bar, and lets the watchdog reset the
meter (which the shim counts, and a second crash inside 60 s enters recovery --
that is the documented policy, not a bug).
"""

import io
import os
import sys

SRC = sys.argv[1]
MAIN = os.path.join(SRC, "main.rs")

t = io.open(MAIN, encoding="utf-8").read()

old = '''    // Frozen, but alive: keep the watchdog fed so the screen stays up.
    loop {
        crate::wdt::kick();
        mmio::spin(200_000);
    }
}'''
new = '''    wait_for_watchdog()
}'''
if old not in t:
    sys.exit("freeze loop not found")
t = t.replace(old, new)

t = t.replace("fn panic(info: &PanicInfo) -> ! {", "fn panic(_info: &PanicInfo) -> ! {")
t = t.replace("    // Diagnostic: freeze instead of resetting, so the marker can be read later.\n    // The buzzer is silenced first (TIM14 keeps running through a panic).",
              "    // The buzzer is silenced first (TIM14 keeps running through a panic);\n    // then the bar marks the crash and the watchdog resets the meter.")
io.open(MAIN, "w", encoding="utf-8", newline="\n").write(t)
sys.stderr.write("shipping panic handler restored\n")
