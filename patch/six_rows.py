import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# six rows fill the panel now that the position line is gone
sub("pub const SET_SHOWN: usize = 5;", "pub const SET_SHOWN: usize = 6;", "shown")

# drop the "a-b/25" line
start = t.find("    // Position, so the hidden rows are obvious.")
if start >= 0:
    end = t.find("\n}\n", start)
    t = t[:start] + "\n" + t[end + 1:]

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("six rows, no position line")
