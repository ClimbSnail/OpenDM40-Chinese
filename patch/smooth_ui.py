import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (t.count(old), old[:60]))
    t = t.replace(old, new)


sub("""/// The settings list scrolls: this many of `SETTINGS` are on screen, the
/// rest are reached by swiping the page up / down.
pub const SET_SHOWN: usize = 5;""",
    """/// The settings list scrolls: this many rows are on screen at once, and one
/// more is drawn while the list sits between two rows (smooth scrolling).
pub const SET_SHOWN: usize = 5;
pub const SET_DRAWN: usize = SET_SHOWN + 1;
/// Row pitch of the settings list, in pixels (see SB_PITCH).
pub const SET_PITCH_PX: i16 = 46;""")

# settings(): rows offset by a sub-row amount
sub("""/// Settings list starting at row `top`: five big rows, plus the position of
/// the window at the bottom. `vals` holds the five visible rows.
pub fn settings(top: u8, vals: &[&str]) {
    let top = top as usize;""",
    """/// Settings list starting at row `top`, shifted up by `frac` pixels (0..46):
/// the list scrolls smoothly rather than a row at a time. `vals` holds the
/// six rows that can be visible, the last one only partly.
pub fn settings(top: u8, frac: i16, vals: &[&str]) {
    let top = top as usize;
    let frac = frac.clamp(0, SET_PITCH_PX - 1);""")

sub("""    for i in 0..SET_SHOWN {
        let g = top + i;
        if g >= SETTINGS.len() {
            break;
        }""",
    """    for i in 0..SET_DRAWN {
        let g = top + i;
        if g >= SETTINGS.len() {
            break;
        }""")

sub("""        let r = set_row_big(i);
        sf::rbox(r, 8, bg, M_BG);""",
    """        let mut r = set_row_big(i);
        r.y -= frac;
        sf::rbox(r, 8, bg, M_BG);""")

sub("""    for g in SET_STEP_ROWS {
        if g >= top && g < top + SET_SHOWN {
            if let Some(v) = vals.get(g - top) {
                set_stepper_at(set_row_big(g - top), g - top, v, STEP_MINUS_X);
            }
        }
    }""",
    """    for g in SET_STEP_ROWS {
        if g >= top && g < top + SET_DRAWN {
            if let Some(v) = vals.get(g - top) {
                let mut r = set_row_big(g - top);
                r.y -= frac;
                set_stepper_at(r, g - top, v, STEP_MINUS_X);
            }
        }
    }""")

# hit: the same shift
sub("""fn list_hit_big(y: u16) -> Option<usize> {
    let y = y as i16;
    for i in 0..SET_PER_PAGE {
        let top = SB_Y0 + i as i16 * SB_PITCH;
        if y >= top && y < top + SB_PITCH {
            return Some(i);
        }
    }
    None
}""",
    """fn list_hit_big(y: u16, frac: i16) -> Option<usize> {
    let y = y as i16 + frac.clamp(0, SET_PITCH_PX - 1);
    for i in 0..SET_DRAWN {
        let top = SB_Y0 + i as i16 * SB_PITCH;
        if y >= top && y < top + SB_PITCH {
            return Some(i);
        }
    }
    None
}""")

sub("""pub fn settings_hit(y: u16) -> Option<usize> {
    list_hit_big(y)""",
    """pub fn settings_hit(y: u16, frac: i16) -> Option<usize> {
    list_hit_big(y, frac)""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ui.rs: sub-row scrolling")
