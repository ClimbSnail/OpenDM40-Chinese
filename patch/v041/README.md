# patch/v041 —— v0.4.1 汉化流水线

这套脚本把上游 **v0.4.1** 的英文源码变成 `firmware/DM40_v0.4.1.01.BIN`。
和 v0.3.0 时代的 `mkpatch*.py` 不同，这里**不是**几百个锚点补丁，而是
"一份词典 + 一步替换"，因为 v0.4.0/zh9/zh10 的锚点补丁脚本当年没入库（放在作者本地
`4-工具/`，已丢失），只能重建。

## 流程

```
zh10 镜像（v0.4.0 汉化版，加密）
        │  stock/dm40fw.py unpack
        ▼
   明文镜像 ── 抽中文串 ──┐
                          ├─ 人工补译 ─→ zh_manual.tsv
v0.4.0 英文镜像（自建）── 抽英文串 ─┘        │
        ▲                                    ▼
        │                          zh_dict.csv（唯一事实源）
   v0.4.0 源码 ──── 词典候选 ────────────────┘
                                                │
v0.4.1 源码 ── apply_dict.py ◀──────────────────┘
        │
        ├─ splash_center.py → 开机画面整块垂直居中（TOP 84 → 132）
        ├─ dialog_font.py → 弹窗/提示条按内容选字面（中文走 TEXT22）
        ├─ vendor_name.py → 设备信息页厂商行「正点原子 & 蜗牛」
        ├─ derive_sets.py → keep_cjk.txt / need_glyphs.txt（汉字 + 全角标点）
        ├─ rebuild_fonts.py → stockfont_data.rs（16 px，353 字）
        └─ build_zh.sh → cargo build + dm40fw.py pack --pad
```

## 各脚本

| 脚本 | 作用 |
|---|---|
| `harvest_patches.py` | 从 v0.3.0 的 `mkpatch*.py`（已归档到 `patch/legacy-v030/`，用 `--patch-dir` 指过去）里把 `(英文, 中文)` 对照抽出来（183 条），作为翻译记忆的种子 |
| `extract_strings.py` | 解密/拆包镜像、按源码词典分词抽字符串、双镜像对齐（实验性，见下） |
| `build_dict.py` | 把候选文案与镜像对照，标出 auto/check/todo |
| `make_todo.py` | 汇总本次范围：harvest ∩ v0.4.1、zh10 里确实被翻译过的串、v0.4.1 新增的串 |
| `zh_manual.tsv` | **人工审定**的译文表（英文 → 中文 / keep） |
| `merge_dict.py` | 合并成 `zh_dict.csv`，并把每条中文与 zh10 镜像里的实际用词做双字校验 |
| `apply_dict.py` | 按**整条字符串字面量**替换，不做子串替换；词典里有条目没命中就报错退出 |
| `splash_logo.py` | 把 `patch/splash_img.rs` 接进 v0.4.1：`native.rs` 注册 `splash_img` 子模块，`splash::draw()` 铺完底色后画字标；幂等，锚点必须唯一命中 |
| `check_fonts.py` | 静态检查：找出「字面量是中文、字体却没有汉字字形」的行（编译不会报错，屏上是空白） |
| `font_fix.py` | 把上一步查出的行改画到 `sf::TEXT22`，只动字体与两处 14 px 小格的尺寸 |
| `splash_center.py` | 开机画面整块居中：`splash.rs` 的 `TOP` 84 → 132，配合同步下移的字标（`gen_splash_img2.py` 的 `Y = TOP - H - 19`），上下各留 66 px |
| `dialog_font.py` | 弹窗/提示条（`dialog.rs`，以及图库的确认框）按内容选字面：ASCII 用原厂 26 px `ASCII26`，含中文就换 `TEXT22`。`ASCII26` 没有汉字，译文走它就是一整块空白 |
| `vendor_name.py` | 把设备信息页的厂商行改成本项目的标记（`--value`，默认 `正点原子 & 蜗牛`）；整行匹配、命中必须为 1，换标记只要换 `--value` 重跑。这不是翻译，所以不进 `zh_dict.csv` |
| `preview_text.py` | 离线渲染：解码生成的 `stockfont_data.rs`（BIT1），按固件的排版算术画成 PNG，用真实字库量宽度、拼开机整帧 |
| `build_fix_windows.py` | Windows 构建修复：`stackdepth.py` 找 `llvm-objdump` 缺 `.exe`；`build.sh` 的 `rm -f` 在本机被安全删除钩子拦下，改成截断 + `-s` 判断 |
| `build_zh.sh` | 一键构建（设置 `RUSTUP_HOME`/`PATH`/`DM40_VERSION_SUFFIX`） |

## 词典

`zh_dict.csv` 共 386 条：361 条有中文、25 条 `keep`（故意保留英文）。
`keep` 的都是**刷不出来的**：

- SCPI 关键字、`DC`/`AC`、`UART/8N1`、`FFT`、`dB/div` —— 规范要求英文；
- 用 `b"..."` 字节串 + 小字号（12 px / `SC_F16`）画的行 —— 那两套字体**没有汉字字形**，
  硬塞只会花屏。想汉化得先改字号或用 `TEXT22`。

`status` 列的含义：`harvest`（v0.3.0 沿用的译文）、`manual`（本次人工译）、
`manual-new`（v0.4.1 新增文案）、`keep`（保留英文）。

## 镜像对齐（为什么最后靠人工）

`extract_strings.py` + `align_bootstrap.py` 的思路是：两版镜像里 ASCII 字面量不变，
用它们当锚点，把中文串和英文串按地址顺序配对。实测结论：

- **顺序基本稳定**：811 个"两侧都唯一"的 ASCII 串里有 801 个位置一致（99%），
  说明单 CGU + LTO 的 rodata 顺序大体可比；
- **但配对不能自动**：rustc 会把相邻字面量首尾相接，几个中文串粘成一串
  （`厂商正点原子型号` = 厂商 + 正点原子 + 型号），拆分需要中文字典，
  而字典正是要得到的东西 —— 自举收敛不了。

所以最终采用：**镜像只用来定"范围"和"用词"**（`docs/` 里记录了每个词的来源），
译文由 `zh_manual.tsv` 人工审定。`merge_dict.py` 会用双字覆盖度把与 zh10 用词不一致的
条目列出来（当前 27 条，多为 v0.4.1 新增文案或跨字面量的拼接项）。

## 字体

- 汉字统一 **16 px**（v0.4.0-zh 的结论：22 px 装不下，17.8 KB → 11.8 KB）。
- 字形格 **16×16**（`--txt22-adv 16`）：22 px 宽的格子里塞 16 px 字，每字白扔 6 列空白。
- 只保留 ASCII 等原厂字形（不裁 Latin，v0.4.0 的教训：裁掉的字会显示成方框）。
- 353 个字形（345 汉字 + `：，？！（）…、` 8 个全角标点）≈ 13.9 KB，B 区余量 4,224 字节。

## 待办（本版没做）

1. **版面精修**：v0.4.0-zh 做过的"设置页单页滚动/六行、弹窗满宽、触发页两行"等版面改动，
   本次没搬（改为沿用 v0.4.1 的分页设置）。中文比英文窄，不会溢出，但视觉密度不如 zh10。
2. **自有功能**：~~开机画面~~ 已补（`splash_logo.py`，字标为 **Snail**，134×47，
   A2 只剩 1,524 字节，放大图片前先看预算）；**图库跨页多选批量删除**、
   **充电指示白框绿格外观** 两项仍是上游原样
   （充电判定逻辑本身上游 v0.4.1 已吸收本项目的压降实测）。
3. **真机验证**：本版未上真机；模拟器需要私有 flash dump，本机没有。
4. `docs/opendm40-中文使用说明书.md` 尚未按 v0.4.1 的行为差异修订。
