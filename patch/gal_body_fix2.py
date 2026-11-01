import io

# --- 1. undo the font move: K_FONT_B back into region B -------------------
L = r"F:\desk\study\build\opendm40-0.3.0\firmware\link-native.x"
x = io.open(L, encoding="utf-8").read()

# take it out of the cold list
a = "        *(.rodata.fonts.K_FONT_B);\n"
if x.count(a) != 1:
    raise SystemExit("cold K_FONT_B %d" % x.count(a))
x = x.replace(a, "")
# and put it back where it was (the region B font block, after ICONS_B)
b = "        *(.rodata.fonts.ICONS_B);\n"
if x.count(b) != 1:
    raise SystemExit("ICONS_B %d" % x.count(b))
x = x.replace(b, b + a)
# floors back to sane values
x = x.replace("ASSERT(0x080A0000 - __image_end >= 0", "ASSERT(0x080A0000 - __image_end >= 3400")
io.open(L, "w", encoding="utf-8", newline="\n").write(x)

# --- 2. the dialog body: a static phrase, no formatting ------------------
P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\gallery.rs"
t = io.open(P, encoding="utf-8").read()
i = t.find("            Dlg::DelSel => {")
j = t.find("            Dlg::Delete | Dlg::Deleting =>", i)
if i < 0 or j < 0:
    raise SystemExit("delsel block not found")
NEW = """            Dlg::DelSel => {
                // The body is a fixed phrase: Tb can only carry ASCII, and
                // formatting the count by hand costs more code than the
                // region has left.
                dialog_box("\u5220\u9664\u6240\u9009", "\u786e\u5b9a\u5220\u9664", Some("\u5220\u9664"))
            }
"""
t = t[:i] + NEW + t[j:]
io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("reverted the font move; body is a static phrase")
