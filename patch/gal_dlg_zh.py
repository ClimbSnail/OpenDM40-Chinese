import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# the two confirm titles were still English
sub('let t = if self.cur.kind == Kind::Csv { "Delete this log?" } else { "Delete screenshot?" };',
    'let t = if self.cur.kind == Kind::Csv { "删除这条记录？" } else { "删除这张截图？" };',
    "titles")

# the dialogs do take taps after all: ask before wiping a selection
sub("""                        if self.sel_n > 0 {
                            // No confirm box: the gallery's dialog boxes do
                            // not take taps on this unit, and a dead dialog
                            // would strand the screen.
                            self.mode = Mode::Dialog;
                            self.dlg = Dlg::Deleting;
                            self.sel_pending = true;
                            self.need |= N_DEL;
                        }""",
    """                        if self.sel_n > 0 {
                            // Confirm first: the dialog boxes do take taps
                            // (verified 2026-11-01).
                            self.mode = Mode::Dialog;
                            self.dlg = Dlg::DelSel;
                            self.paint |= P_DLG;
                        }""",
    "confirm")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("dialog titles localized, batch confirm restored")
