import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("ui %d: %r" % (t.count(old), old[:60]))
    t = t.replace(old, new)


sub("pub fn settings(top: u8, frac: i16, vals: &[&str]) {",
    "pub fn settings(top: u8, frac: i16, vals: &[&str], with_title: bool) {")

sub("""    let only = row_only();
    if only.is_none() {
        page_title("设置");
        lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, lcd::H - PAGE_BAR_H as u16, M_BG);
    }""",
    """    let only = row_only();
    if only.is_none() {
        if with_title {
            page_title("设置");
            lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, lcd::H - PAGE_BAR_H as u16, M_BG);
        } else {
            // Scrolling: only the list band is cleared, the title bar and the
            // position line are left alone (a full clear every frame flickers).
            lcd::fill_rect(0, PAGE_BAR_H as u16, lcd::W, (PAGE_KEY_Y - PAGE_BAR_H) as u16, M_BG);
        }
    }""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub2(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("app %d: %r" % (t.count(old), old[:60]))
    t = t.replace(old, new)


sub2("ui::settings(top as u8, self.set_frac_now(), &all[top..hi]);",
     "ui::settings(top as u8, self.set_frac_now(), &all[top..hi], self.set_drag0 < 0);")

sub2("""            Gesture::Drag(a, b, _) if self.view == View::Settings => {
                if self.set_drag0 < 0 {
                    self.set_drag0 = self.scroll_px();
                }
                self.set_scroll_px(self.set_drag0 + a.y as i16 - b.y as i16);
            }""",
     """            Gesture::Drag(a, b, _) if self.view == View::Settings => {
                if self.set_drag0 < 0 {
                    self.set_drag0 = self.scroll_px();
                }
                // One repaint per 6 px: every drag event repainting the page
                // made the screen flicker.
                let want = self.set_drag0 + a.y as i16 - b.y as i16;
                if (want - self.scroll_px()).abs() >= 6 {
                    self.set_scroll_px(want);
                }
            }""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("throttle + partial repaint")
