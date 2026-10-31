import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("anchor missing (%d): %r" % (t.count(old), old[:70]))
    t = t.replace(old, new)


# ---------- draw: one value table, the visible window --------------------
s = t.find("            View::Settings => {\n                let p = self.set_page.min(ui::SET_PAGES - 1);")
e = t.find("            View::Gallery => crate::gallery::get().draw(),")
if s < 0 or e < s:
    raise SystemExit("draw block not found")

draw = '''            View::Settings => {
                let mut b0 = [0u8; 8];
                let mut b1 = [0u8; 8];
                let mut ab = [0u8; 16];
                let mut vb = [0u8; 40];
                let pct = |b: &mut [u8; 8], v: u8| -> usize {
                    let mut t = [0u8; 16];
                    let s = crate::dmm::format(&mut t, v as f32, 0);
                    b[..s.len()].copy_from_slice(s.as_bytes());
                    b[s.len()] = b'%';
                    s.len() + 1
                };
                let n0 = pct(&mut b0, self.backlight);
                let n1 = pct(&mut b1, self.volume);
                self.usb_ro_drawn = usb_ro();
                let all: [&str; 25] = [
                    DIM_TXT[self.dim_idx],
                    if self.dim_glow { "微光" } else { "全黑" },
                    OFF_TXT[self.off_idx],
                    core::str::from_utf8(&b0[..n0]).unwrap_or(""),
                    core::str::from_utf8(&b1[..n1]).unwrap_or(""),
                    if self.bt_on { "开" } else { "关" },
                    ui::view_name(START[self.start_page]),
                    if self.rails_both { "两者常开" } else { "自动 (按视图)" },
                    {
                        // Rate, with the measured readings/s (FR-05).
                        let mut rb = [0u8; 16];
                        let rps = ui::rps_text(&mut rb, self.dmm.reading_period_ms());
                        let applies = self.dmm.rate_applies();
                        let mut n = 0;
                        for part in [
                            ["慢", "中", "快"][self.dmm.rate() as usize],
                            if applies { "  " } else { " (n/a here)" },
                            if applies { rps } else { "" },
                        ] {
                            let k = part.len().min(40 - n);
                            vb[n..n + k].copy_from_slice(&part.as_bytes()[..k]);
                            n += k;
                        }
                        core::str::from_utf8(&vb[..n]).unwrap_or("")
                    },
                    crate::meter::SMOOTH_NAMES[self.meter.smoothing() as usize],
                    if self.dmm_view.bar_on { "柱状图" } else { "历史" },
                    if self.dmm.temp_f() { "华氏" } else { "摄氏" },
                    if self.sp.swipes { "顶栏" } else { "关 (原厂)" },
                    if self.sp.press_fx { "开" } else { "关 (原厂)" },
                    crate::scope_ui::TAP_NAMES[self.sp.tap_mode.min(2) as usize],
                    if gesture::grab_ms() == 0 {
                        scope_page::DRAG_NAMES[self.sp.drag_mode.min(1) as usize]
                    } else {
                        "按住"
                    },
                    alert_mask_name(&mut ab, self.dmm.alert_mask()),
                    crate::danger::NAMES[self.alarm_mode.min(2) as usize],
                    ui::usb_disk_name(self.usb_ro_drawn.0, self.usb_ro_drawn.1),
                    if self.dmm.burden_show { "开 (A, mA, uA)" } else { "关 (原厂)" },
                    "", // Device: opens the About page
                    "", // Touch test: opens the page
                    if self.dmm_view.acc_on { "开" } else { "关" },
                    if self.dmm.ohm_neg { "开" } else { "关 (原厂)" },
                    BUZZ_TXT[self.buzz_idx.min(4)],
                ];
                let top = self.set_top();
                ui::settings(top as u8, &all[top..top + ui::SET_SHOWN]);
            }
'''
t = t[:s] + draw + t[e:]

# ---------- hit: scroll offset + slot -----------------------------------
sub('''                if let Some(next) = ui::settings_nav_hit(x, y) {
                    if next {
                        if self.set_page + 1 < ui::SET_PAGES {
                            self.set_page += 1;
                        }
                    } else if self.set_page > 0 {
                        self.set_page -= 1;
                    }
                    self.redraw = true;
                    return;
                }
                let Some(row) = ui::settings_hit(y) else { return };
                match self.set_page as usize * ui::SET_PER_PAGE + row {''',
    '''                let Some(row) = ui::settings_hit(y) else { return };
                match self.set_top() + row {''')

# the title bar no longer pages: it just leaves
sub('''                if ui::title_back_hit(y) {
                    // Title bar: back a page, or out to the menu from page 1.
                    if self.set_page == 0 {
                        self.show(View::Menu, clk);
                    } else {
                        self.set_page -= 1;
                        self.redraw = true;
                    }
                    return;
                }''',
    '''                if ui::title_back_hit(y) {
                    self.show(View::Menu, clk);
                    return;
                }''')

# ---------- swipes scroll the list --------------------------------------
sub('''            // One finger down the DMM page: start / stop the CSV recording.
            Gesture::SwipeDown if self.view == View::Dmm => self.rec_toggle(now),''',
    '''            // One finger down the DMM page: start / stop the CSV recording.
            Gesture::SwipeDown if self.view == View::Dmm => self.rec_toggle(now),
            // The settings list scrolls one row per swipe.
            Gesture::SwipeUp if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 + 1);
            }
            Gesture::SwipeDown if self.view == View::Settings => {
                self.set_scroll(self.set_page as i16 - 1);
            }''')

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("app.rs: scrolling settings")
