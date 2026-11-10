import io

P = r"F:\desk\study\build\opendm40-0.3.0\firmware\src\ui_power.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# "shunt" -> 分流, in the 22 px font so the hanzi exist
sub('sf::label(sf::F14, rect(SHUNT.x + SHUNT.w + 4, SHUNT.y + 7, 44, 14), "shunt", DIM, DLG_BODY, 0, 1);',
    'sf::label(sf::TEXT22, rect(SHUNT.x + SHUNT.w + 4, SHUNT.y + 1, 44, 24), "分流", DIM, DLG_BODY, 0, 1);',
    "shunt")

# the note line, 22 px Chinese instead of two 14 px English ones
sub('''    sf::label(sf::F14, rect(x + 16, 222, w - 32, 14), "COM carries the load current; P > 0: I into A", STATUS_FG, DLG_BODY, 8, 1);
    sf::label(sf::F14, rect(x + 16, 240, w - 32, 14), t.s(), VALUE, DLG_BODY, 8, 1);''',
    '''    sf::label(sf::TEXT22, rect(x + 16, 214, w - 32, 26), "电流经 COM 与 A 表笔", STATUS_FG, DLG_BODY, 8, 0);
    sf::label(sf::F14, rect(x + 16, 244, w - 32, 14), t.s(), VALUE, DLG_BODY, 8, 1);''',
    "note")

# the rating line drops its English words: numbers only
sub('''    t.push("Max 10 A; above ").push(sig_text(&mut b, i_cont, 2)).push(" A: ");''',
    '''    t.push(sig_text(&mut b, i_cont, 2)).push(" A");''', "rating 1")
sub('''        t.push(crate::dmm::format(&mut b2, t_lim as f32, 0)).push(" s");
    } else {
        t.push("no limit");
    }''',
    '''        t.push(" / ").push(crate::dmm::format(&mut b2, t_lim as f32, 0)).push(" s");
    }''', "rating 2")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("wiring dialog localized")
