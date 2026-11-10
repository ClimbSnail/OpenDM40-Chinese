#!/usr/bin/env python3
"""Diagnostic build: freeze on panic and paint the line number in binary.

Two changes, both temporary:

1. `rec_toggle` goes back to the real implementation (the earlier build stubbed
   it out to "记录暂不可用" so the meter would stop crashing). We need the
   gesture to reproduce.

2. The panic handler stops before feeding nothing: it paints the magenta bar,
   then draws 16 squares along it -- bit b of `info.location().line()`, LSB on
   the left, black = 1 -- and then feeds the watchdog forever. A frozen screen
   keeps the evidence; the previous build reset after ~2 s and lost it.

    python diag_panic.py FIRMWARE_SRC_DIR
"""

import io
import os
import sys

SRC = sys.argv[1]
APP = os.path.join(SRC, "app.rs")
MAIN = os.path.join(SRC, "main.rs")

app = io.open(APP, encoding="utf-8").read()

# ---- 1. re-enable the recording gesture ------------------------------
stub = "    #[allow(dead_code)]\n    fn rec_toggle_disabled(&mut self, now: u64) {"
if stub not in app:
    sys.exit("stub not found")
app = app.replace(stub, "    fn rec_toggle_real(&mut self, now: u64) {")

# drop the stub body of rec_toggle and forward to the real one
old = '''    fn rec_toggle(&mut self, now: u64) {
        // CSV 记录暂停：停止记录时 csvlog 的收尾会把主循环卡住，看门狗复位；
        // 连续两次就进原厂恢复模式。定位到真正原因前先挡住手势，
        // 不让表反复重启。
        self.toast(now, "记录暂不可用", false);
        self.beep(now, 300);
    }'''
new = '''    fn rec_toggle(&mut self, now: u64) {
        // Diagnostic build: the real thing, so the stop crash can be caught.
        self.rec_toggle_real(now)
    }'''
if old not in app:
    sys.exit("stub body not found")
app = app.replace(old, new)
io.open(APP, "w", encoding="utf-8", newline="\n").write(app)

# ---- 2. the diagnostic panic handler --------------------------------
main = io.open(MAIN, encoding="utf-8").read()
start = main.find("#[panic_handler]")
if start < 0:
    sys.exit("panic handler not found")
end = main.find("\n}", main.find("wait_for_watchdog()", start))
end = main.find("\n", end + 1)

new_handler = '''#[panic_handler]
fn panic(info: &PanicInfo) -> ! {
    // Diagnostic: freeze instead of resetting, so the marker can be read later.
    // The buzzer is silenced first (TIM14 keeps running through a panic).
    const TIM14_CCR1: u32 = 0x4000_2000 + 0x34;
    unsafe {
        core::ptr::write_volatile(TIM14_CCR1 as *mut u32, 0);
    }
    lcd::fill_rect(0, lcd::H - 24, lcd::W, 24, lcd::MAGENTA);

    // 16 squares: bit b of the failing line, LSB left, black = 1.
    let mut code = 0u32;
    if let Some(loc) = info.location() {
        code = loc.line();
    }
    let mut b = 0;
    while b < 16 {
        let on = (code >> b) & 1 != 0;
        let x = 8 + b * 14;
        lcd::fill_rect(x as u16, lcd::H - 20, 10, 16, if on { lcd::BLACK } else { lcd::MAGENTA });
        b += 1;
    }
    // Frozen, but alive: keep the watchdog fed so the screen stays up.
    loop {
        crate::wdt::kick();
        mmio::spin(200_000);
    }
}
'''
main = main[:start] + new_handler + main[end + 1:]
io.open(MAIN, "w", encoding="utf-8", newline="\n").write(main)
sys.stderr.write("diagnostic build ready\n")
