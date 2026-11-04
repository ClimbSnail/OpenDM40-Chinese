import io
import re

S = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src"


def rd(p):
    return io.open(S + "\\" + p, encoding="utf-8").read()


def wr(p, t):
    io.open(S + "\\" + p, "w", encoding="utf-8", newline="\n").write(t)


# ---------------- ui.rs ----------------
u = rd("ui.rs")

# 1. 枚举变体 + 注释
u = u.replace("""    /// On-device help (UF-29), Settings 2/3 -> Help: HELP pages.
    Help,
""", "")

# 2. 标题
u = u.replace('        View::Help => "帮助",\n', "")

# 3. HELP 表 + help_page + 两个常量（删到 device_page 之前）
i = u.find("/// On-device help (UF-29: owners have no manual")
j = u.find("/// opendm40 firmware version (ident.rs")
if i > 0 and j > i:
    u = u[:i] + u[j:]
    print("ui.rs: 删掉 HELP 表与 help_page")
else:
    print("ui.rs: 帮助代码块没找到", i, j)

wr("ui.rs", u)

# ---------------- app.rs ----------------
a = rd("app.rs")

a = a.replace("View::Gallery | View::Help | View::Inrush", "View::Gallery | View::Inrush")
a = a.replace("        View::Help => ui::help_page(self.help_page),\n", "")
a = a.replace("                    View::Help => View::Settings,\n", "")
a = a.replace("""            View::Help => {
                // Title bar: back to Settings 2/2 (as MENU); elsewhere: the
                // next help page (wraps).
                if ui::title_back_hit(y) {
                    self.show(View::Settings, clk);
                } else {
                    self.help_page = (self.help_page + 1) % ui::HELP.len();
                    self.redraw = true;
                }
            }
""", "")
a = a.replace("    /// Help page shown (UF-29, ui::HELP index).\n    help_page: usize,\n", "")
a = a.replace("        help_page: 0,\n", "")

wr("app.rs", a)
print("app.rs: 移除 View::Help 的所有分支")

# 检查残留
for f in ("ui.rs", "app.rs", "app_press.rs", "gesture.rs"):
    t = rd(f)
    n = len(re.findall(r"Help|help_page", t))
    if n:
        print("  %s 还有 %d 处提到 Help" % (f, n))
