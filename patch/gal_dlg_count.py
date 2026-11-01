import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# back to the plain blue title bar
sub("""    if title.is_empty() {
        lcd::fill_rect(b.0, b.1, b.2, 40, D_BODY);
    } else {
        lab((b.0, b.1, b.2, 40), title, D_TITLE);
    }
    lab((b.0, b.1 + 40, b.2, 60), body, D_BODY);""",
    """    lab((b.0, b.1, b.2, 40), title, D_TITLE);
    lab((b.0, b.1 + 40, b.2, 60), body, D_BODY);""",
    "bar")

# the body now says how many files are going
sub('            Dlg::DelSel => {\n                dialog_box("", "删除所选", Some("删除"))\n            }',
    """            Dlg::DelSel => {
                let mut tb = Tb::new();
                tb.s("已选 ");
                tb.u(self.sel_n as u32);
                tb.s(" 个");
                dialog_box("删除所选", tb.str(), Some("删除"))
            }""",
    "delsel")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("title back in the blue bar, count in the body")
