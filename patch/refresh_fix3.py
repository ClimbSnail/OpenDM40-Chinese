import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


sub("""    set_title: bool,""",
    """    set_title: bool,
    /// Repaints still owed to the settings page: a value that depends on the
    /// live state (the rate's readings/s, the USB mode after a re-plug) only
    /// settles a frame or two later, and nothing else would repaint it.
    set_refresh: u8,""", "field")

sub("            set_title: true,", "            set_title: true,\n            set_refresh: 0,", "init")

sub("""        if self.redraw {
            self.repaint(now);
        }""",
    """        if self.view == View::Settings && self.set_refresh > 0 {
            self.set_refresh -= 1;
            self.redraw = true;
        }
        if self.redraw {
            self.repaint(now);
        }""", "poll")

sub("""                let Some(row) = ui::settings_hit(y, frac) else { return };""",
    """                self.set_refresh = 10;
                let Some(row) = ui::settings_hit(y, frac) else { return };""", "tap")

sub("if self.view == View::Settings && self.set_page == 3 && self.usb_ro_drawn != usb_ro() {",
    """if self.view == View::Settings
            && (self.set_page as usize) <= 18
            && 18 < self.set_page as usize + ui::SET_SHOWN
            && self.usb_ro_drawn != usb_ro()
        {""", "usb watch")

sub("self.redraw |= self.view == View::Settings && self.set_page == 3;",
    """self.redraw |= self.view == View::Settings
            && (self.set_page as usize) <= 18
            && 18 < self.set_page as usize + ui::SET_SHOWN;""", "usb redraw")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("ok")
