import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (t.count(old), old[:70]))
    t = t.replace(old, new)


# ---- drop the pager keys: one scrolling list instead --------------------
sub('''/// Pager keys in their own row: "< 上一页" left, "下一页 >" right.
const PAGE_KEY_W: i16 = 156;
const PAGE_KEY_H: i16 = 38;
const PAGE_KEY_Y: i16 = 270;

fn page_key(next: bool) -> sf::Rect {
    let x = if next { 480 - 8 - PAGE_KEY_W } else { 8 };
    rect(x, PAGE_KEY_Y, PAGE_KEY_W, PAGE_KEY_H)
}

/// Tap on the pager row: Some(false) = previous page, Some(true) = next.
pub fn settings_nav_hit(x: u16, y: u16) -> Option<bool> {
    let (px, py) = (x as i16, y as i16);
    for next in [false, true] {
        let r = page_key(next);
        if px >= r.x && px < r.x + r.w && py >= r.y && py < r.y + r.h {
            return Some(next);
        }
    }
    None
}

''', """/// The settings list scrolls: this many of `SETTINGS` are on screen, the
/// rest are reached by swiping the page up / down.
pub const SET_SHOWN: usize = 5;

""")

# ---- settings(): a window onto the whole list ---------------------------
start = t.find("/// Settings page `page` (0..SET_PAGES-1) with its five row values.")
end = t.find("/// A settings-style page: title bar with \"< Back\"")
if start < 0 or end < start:
    raise SystemExit("settings() block not found")

new = '''/// Settings list starting at row `top`: five big rows, plus the position of
/// the window at the bottom. `vals` holds the five visible rows.
pub fn settings(top: u8, vals: &[&str]) {
    let top = top as usize;
    let only = row_only();
    if only.is_none() {
        page_title("设置");
        lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, lcd::H - PAGE_BAR_H as u16, M_BG);
    }
    for i in 0..SET_SHOWN {
        let g = top + i;
        if g >= SETTINGS.len() {
            break;
        }
        // Pressed: the keypads' pressed colour, the value white on it.
        let (bg, vfg) = match only {
            None => (M_TILE, M_ACCENT),
            Some(q) if q.row as usize == i && q.part == 0 => {
                if q.on { (K_SEL, STATUS_FG) } else { (M_TILE, M_ACCENT) }
            }
            Some(_) => continue,
        };
        let r = set_row_big(i);
        sf::rbox(r, 8, bg, M_BG);
        sf::glyphs(sf::TEXT22, rect(r.x + 12, r.y, 190, r.h), SETTINGS[g], STATUS_FG, bg, 1, 0);
        if SET_STEP_ROWS.contains(&g) {
            continue; // the stepper draws "-", the value and "+"
        }
        let v = vals.get(i).copied().unwrap_or("");
        sf::glyphs(sf::TEXT22, rect(r.x + 202, r.y, 250, r.h), v, vfg, bg, 1, 0);
    }
    for g in SET_STEP_ROWS {
        if g >= top && g < top + SET_SHOWN {
            if let Some(v) = vals.get(g - top) {
                set_stepper_at(set_row_big(g - top), g - top, v, STEP_MINUS_X);
            }
        }
    }
    // Position, so the hidden rows are obvious.
    if only.is_none() {
        let first = top + 1;
        let last = (top + SET_SHOWN).min(SETTINGS.len());
        let mut b = [0u8; 24];
        let mut n = 0;
        let mut put = |v: usize, b: &mut [u8; 24], n: &mut usize| {
            let mut d = [0u8; 4];
            let mut k = 0;
            let mut x = v;
            if x == 0 {
                d[0] = b'0';
                k = 1;
            }
            while x > 0 {
                d[k] = b'0' + (x % 10) as u8;
                x /= 10;
                k += 1;
            }
            for j in 0..k {
                b[*n] = d[k - 1 - j];
                *n += 1;
            }
        };
        put(first, &mut b, &mut n);
        b[n] = b'-';
        n += 1;
        put(last, &mut b, &mut n);
        b[n] = b'/';
        n += 1;
        put(SETTINGS.len(), &mut b, &mut n);
        let s = core::str::from_utf8(&b[..n]).unwrap_or("");
        sf::glyphs(sf::TEXT22, rect(0, PAGE_KEY_Y, 480, PAGE_KEY_H),
                   s, 0x8C71, M_BG, 8, 0);
    }
}

'''
t = t[:start] + new + t[end:]

# PAGE_KEY_Y / PAGE_KEY_H are still used for the position line
sub('''/// The settings list scrolls: this many of `SETTINGS` are on screen, the
/// rest are reached by swiping the page up / down.
pub const SET_SHOWN: usize = 5;''',
    '''/// The settings list scrolls: this many of `SETTINGS` are on screen, the
/// rest are reached by swiping the page up / down.
pub const SET_SHOWN: usize = 5;
/// Row of the "first-last/total" position line under the list.
const PAGE_KEY_Y: i16 = 272;
const PAGE_KEY_H: i16 = 30;''')

# ---- hit: slots, the caller adds the scroll offset ---------------------
sub('''pub fn settings_hit(y: u16) -> Option<usize> {
    // The whole pitch is a hit, gaps included, so a tap between two rows
    // still lands on one of them.
    list_hit_big(y)''',
    '''pub fn settings_hit(y: u16) -> Option<usize> {
    list_hit_big(y)''')

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: scrolling list")
