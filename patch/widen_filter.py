import io

P = r"F:\desk\study\DM40-中文固件\8-构建\derive_sets.py"
t = io.open(P, encoding="utf-8").read()

old = '''            if "\\u4e00" <= ch <= "\\u9fff" and ch not in seen:
                seen.append(ch)'''
new = '''            if _wanted(ch) and ch not in seen:
                seen.append(ch)'''
assert old in t, "锚点没找到"
t = t.replace(old, new)

helper = '''
def _wanted(ch):
    """CJK ideographs plus the full-width punctuation the literals use."""
    o = ord(ch)
    return (0x4E00 <= o <= 0x9FFF        # hanzi
            or 0x3000 <= o <= 0x303F    # 。、，etc.
            or 0x2010 <= o <= 0x205E    # … — etc.
            or 0xFF00 <= o <= 0xFFEF)   # ？：，etc. (full-width forms)


'''
if "_wanted" not in t.split("seen = []")[0]:
    t = t.replace("seen = []", helper.lstrip("\n") + "seen = []", 1)

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("derive_sets.py 已放宽字符筛选（汉字 + 全角标点）")
