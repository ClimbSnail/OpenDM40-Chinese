import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (t.count(old), old[:70]))
    t = t.replace(old, new)


sub("""    /// Settings page shown (0 / 1, ui::SETTINGS / SETTINGS2).
    set_page: u8,""",
    """    /// Settings list scroll: first row on screen, its sub-row offset in
    /// pixels, and the scroll the current drag started from (-1: none).
    set_page: u8,
    set_frac: u8,
    set_drag0: i16,""")

sub('''    /// Scroll the settings list to put row `v` first (clamped, redraws).
    fn set_scroll(&mut self, v: i16) {
        let max = ui::SETTINGS.len().saturating_sub(ui::SET_SHOWN) as i16;
        self.set_page = v.clamp(0, max) as u8;
        self.redraw = true;
    }''',
    '''    /// Scroll position of the settings list, in pixels.
    fn scroll_px(&self) -> i16 {
        self.set_page as i16 * ui::SET_PITCH_PX + self.set_frac as i16
    }

    /// Put the settings list at `v` pixels (clamped, redraws).
    fn set_scroll_px(&mut self, v: i16) {
        let max = ui::SETTINGS.len().saturating_sub(ui::SET_SHOWN) as i16 * ui::SET_PITCH_PX;
        let v = v.clamp(0, max);
        self.set_page = (v / ui::SET_PITCH_PX) as u8;
        self.set_frac = (v % ui::SET_PITCH_PX) as u8;
        self.redraw = true;
    }

    /// Scroll the settings list by whole rows (one per swipe).
    fn set_scroll(&mut self, v: i16) {
        let max = ui::SETTINGS.len().saturating_sub(ui::SET_SHOWN) as i16;
        self.set_page = v.clamp(0, max) as u8;
        self.set_frac = 0;
        self.redraw = true;
    }''')

sub("""                let top = self.set_top();
                ui::settings(top as u8, &all[top..top + ui::SET_SHOWN]);""",
    """                let top = self.set_top();
                let hi = (top + ui::SET_DRAWN).min(all.len());
                let frac = if top + ui::SET_SHOWN >= all.len() { 0 } else { self.set_frac as i16 };
                ui::settings(top as u8, frac, &all[top..hi]);""")

sub("""                let Some(row) = ui::settings_hit(y) else { return };
                match self.set_top() + row {""",
    """                let top = self.set_top();
                let frac = if top + ui::SET_SHOWN >= ui::SETTINGS.len() { 0 } else { self.set_frac as i16 };
                let Some(row) = ui::settings_hit(y, frac) else { return };
                match top + row {""")

sub("""            // The settings list scrolls one row per swipe.
            Gesture::SwipeUp if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 + 1);
            }
            Gesture::SwipeDown if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 - 1);
            }""",
    """            // The settings list scrolls one row per swipe ...
            Gesture::SwipeUp if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 + 1);
            }
            Gesture::SwipeDown if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 - 1);
            }
            // ... and follows the finger while it stays down.
            Gesture::Drag(a, b, _) if self.view == View::Settings => {
                if self.set_drag0 < 0 {
                    self.set_drag0 = self.scroll_px();
                }
                self.set_scroll_px(self.set_drag0 + a.y as i16 - b.y as i16);
            }
            Gesture::Up(_) | Gesture::Cancel if self.view == View::Settings => {
                self.set_drag0 = -1;
            }""")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("app.rs updated")
