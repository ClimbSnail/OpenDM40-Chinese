//! Boot splash animation: a scope-like trace sweeps once across the panel
//! while `native::pre_main` starts the disk phases.
//!
//! Lives at the crate root (region B, zero-wait) on purpose: `native::splash`
//! is region C, which has ~64 bytes of headroom left. Called from
//! `native::splash::show` (device only; `draw` is also used by the host
//! renderer, so the animation is not in there).
//!
//! Timing: the DWT cycle counter is enabled here (the same two writes
//! `clock::Clock::new` does later; it resets the counter, so nothing leaks).

use crate::lcd;

const DEMCR: u32 = 0xE000_EDFC;
const DWT_CTRL: u32 = 0xE000_1000;
const DWT_CYCCNT: u32 = 0xE000_1004;
/// HCLK, see clock.rs HCLK_HZ.
const CYC_PER_MS: u32 = 200_000;

/// Trace centre line and half-height: the band 282..310, below the note
/// lines (224..272), so the two never overlap.
const Y_MID: i16 = 296;
const H: i16 = 14;
/// Column step in px and the whole sweep's duration in ms.
const DX: u16 = 2;
const MS: u32 = 200;

#[cfg(not(test))]
pub fn play() {
    use crate::mmio::{modify32, r32, w32};
    use crate::ui::{BG, SEL};

    unsafe {
        modify32(DEMCR, 0, 1 << 24); // TRCENA
        w32(DWT_CYCCNT, 0);
        modify32(DWT_CTRL, 0, 1); // CYCCNTENA
    }
    lcd::fill_rect(0, (Y_MID - H) as u16, lcd::W, (H * 2) as u16, BG);

    let cols = lcd::W as u32 / DX as u32;
    let step_cyc = MS * CYC_PER_MS / cols;
    let mut x = 0u32;
    while x < lcd::W as u32 {
        // A repeating four-step pattern: reads as a signal, costs no table.
        let a = match (x / 6) % 4 {
            0 => H,
            1 => H / 2,
            2 => -H,
            _ => -H / 2,
        };
        let y = Y_MID + a;
        let (y0, h) = if a >= 0 {
            (Y_MID as u16, a as u16)
        } else {
            (y as u16, (-a) as u16)
        };
        lcd::fill_rect(x as u16, y0, 1, h + 2, SEL);
        lcd::fill_rect(x as u16, (y - 1) as u16, DX, 3, SEL);
        let t0 = unsafe { r32(DWT_CYCCNT) };
        while unsafe { r32(DWT_CYCCNT) }.wrapping_sub(t0) < step_cyc {}
        x += DX as u32;
    }
}

#[cfg(test)]
pub fn play() {}
