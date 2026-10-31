import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (t.count(old), old[:70]))
    t = t.replace(old, new)


# MENU leaves the settings page now that it is one scrolling list
sub('''                    View::Settings if self.set_page >= 1 => {
                        self.set_page -= 1;
                        View::Settings
                    }
                    View::Settings => View::Menu,''',
    '''                    View::Settings => View::Menu,''')

# the two scroll helpers, next to the other small App methods
sub('''    /// Save the settings now and then (cheap: 64 words of backup SRAM; the''',
    '''    /// First settings row on screen, clamped so the window always fits.
    fn set_top(&self) -> usize {
        (self.set_page as usize).min(ui::SETTINGS.len().saturating_sub(ui::SET_SHOWN))
    }

    /// Scroll the settings list to put row `v` first (clamped, redraws).
    fn set_scroll(&mut self, v: i16) {
        let max = ui::SETTINGS.len().saturating_sub(ui::SET_SHOWN) as i16;
        self.set_page = v.clamp(0, max) as u8;
        self.redraw = true;
    }

    /// Save the settings now and then (cheap: 64 words of backup SRAM; the''')

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("helpers added")
