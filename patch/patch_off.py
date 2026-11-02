import io

P = r"F:\desk\study\DM40-中文固件\7-源码\opendm40-0.3.0\firmware\src\app.rs"
t = io.open(P, encoding="utf-8").read()


def sub(old, new, tag):
    global t
    if t.count(old) != 1:
        raise SystemExit("%s: %d" % (tag, t.count(old)))
    t = t.replace(old, new)


# 1) 关机档位：永不 + 10..1 小时 + 30/10/5/1 分 = 15 档
sub("const OFF_MS: [u64; 7] = [0, 7_200_000, 3_600_000, 1_800_000, 600_000, 300_000, 60_000];",
    """const OFF_MS: [u64; 15] = [
    0,
    36_000_000, 32_400_000, 28_800_000, 25_200_000, 21_600_000,
    18_000_000, 14_400_000, 10_800_000, 7_200_000, 3_600_000,
    1_800_000, 600_000, 300_000, 60_000,
];""", "OFF_MS")

sub('const OFF_TXT: [&str; 7] = ["永不", "2小时", "1小时", "30分", "10分", "5分", "1分"];',
    '''const OFF_TXT: [&str; 15] = [
    "永不", "10小时", "9小时", "8小时", "7小时", "6小时",
    "5小时", "4小时", "3小时", "2小时", "1小时", "30分", "10分", "5分", "1分",
];''', "OFF_TXT")

# 2) 读回时夹一下：4 bit 能存到 15，而数组只有 15 项（0..14）
sub("        self.dim_idx = (p[0] & 0xF) as usize;",
    "        self.dim_idx = ((p[0] & 0xF) as usize).min(DIM_MS.len() - 1);", "dim clamp")
sub("        self.off_idx = (p[0] >> 4 & 0xF) as usize;",
    "        self.off_idx = ((p[0] >> 4 & 0xF) as usize).min(OFF_MS.len() - 1);", "off clamp")

io.open(P, "w", encoding="utf-8", newline="\n").write(t)
print("关机档位 7 -> 15，并给读回加了夹取")
