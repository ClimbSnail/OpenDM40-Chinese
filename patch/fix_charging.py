import io

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"

# 1) 改充电判定：TP4056 的 /CHRG 低电平 = 正在充电，/STDBY 低电平 = 充满
P = S + r"\power.rs"
t = io.open(P, encoding="utf-8").read()
old = """    pub fn charging(&self) -> bool {
        let b = unsafe { r32(GPIOB + 0x10) };
        b & (1 << 10) != 0 && b & (1 << 11) != 0
    }"""
new = """    /// TP4056 status pins, active low: PB10 = /CHRG (low while charging),
    /// PB11 = /STDBY (low when the charge is complete). Both float high
    /// (pull-ups) with no charger, so "PB10 low, PB11 high" is the only
    /// combination that means charging. 2026-11-03: this was previously
    /// "both high", which is the *idle* state and never showed charging.
    pub fn charging(&self) -> bool {
        let b = unsafe { r32(GPIOB + 0x10) };
        b & (1 << 10) == 0 && b & (1 << 11) != 0
    }"""
if old in t:
    io.open(P, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
    print("power.rs: 充电判定改为 PB10 低 + PB11 高")
else:
    print("power.rs 锚点没找到")

# 2) 撤掉临时调试命令
Q = S + r"\scpi.rs"
s = io.open(Q, encoding="utf-8").read()
import re
before = s
s = re.sub(r'\n *// TEMP 调试：GPIOB 输入电平，看充电检测脚\n *b"GPIO" => [^\n]*\n', "\n", s)
s = re.sub(r'\n *// TEMP 调试：电池电压 mV\n *b"VBAT" => [^\n]*\n', "\n", s)
if s != before:
    io.open(Q, "w", encoding="utf-8", newline="\n").write(s)
    print("scpi.rs: 临时调试命令已删除")
else:
    print("scpi.rs 没有可删的临时命令")

# 3) power.rs 的 VBAT_MV 也去掉
if "VBAT_MV" in io.open(P, encoding="utf-8").read():
    t = io.open(P, encoding="utf-8").read()
    t = t.replace("\n\n/// 最近一次读到的电池电压（毫伏），调试用。\n"
                  "pub static VBAT_MV: core::sync::atomic::AtomicU32 =\n"
                  "    core::sync::atomic::AtomicU32::new(0);", "")
    t = t.replace("\n        VBAT_MV.store((self.vbat * 1000.0) as u32, core::sync::atomic::Ordering::Relaxed);", "")
    io.open(P, "w", encoding="utf-8", newline="\n").write(t)
    print("power.rs: VBAT_MV 已删除")
