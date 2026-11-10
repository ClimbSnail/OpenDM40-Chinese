# patch/ —— 汉化与构建脚本

这里的脚本**不是**给使用者用的，是记录「从 opendm40 原版到中文版」做了哪些改动。
只想刷机看根目录 [README](../README.md)；想自己重建看 [README 的「从源码重建」](../README.md#从源码重建v04101)。

## 目录结构

| 位置 | 内容 |
|---|---|
| [`v041/`](v041/README.md) | **当前流水线**（v0.4.1）：词典 `zh_dict.csv` → `apply_dict.py` 套译文 → 字体/字标/开机居中/弹窗字面 → `build_zh.sh` 出镜像 |
| 本目录 | 流水线共用的字形与字标工具（见下表） |
| [`legacy-v030/`](legacy-v030/README.md) | **历史留档**：v0.3.0 时代的锚点补丁（`mkpatch*.py` 等 115 个文件）。只对 v0.3.0 源码有效，**不要拿它打 v0.4.x**；留着是因为 `v041/harvest_patches.py` 要从中复现词典里那批译文的来源 |

## 共用工具

| 文件 | 作用 |
|---|---|
| `derive_sets.py` | 扫源码里的字符串字面量，产出下面两个字形清单：汉字 + 全角标点 `：，？！（）…、` |
| `rebuild_fonts.py` | 按清单重建 `stockfont_data.rs`（TEXT22 与 F14 的编码约定相反，见脚本头注释）|
| `gen_splash_img2.py` | 渲染开机字标 → `splash_img.rs`（默认 `Snail` 58 px，自动裁切、打包、核对 A2 预算）|
| `splash_img.rs` | 生成好的开机字标位图（134×47 单色，799 字节，放 A2 区）|
| `ascii_keep.py` / `ascii_keep.txt` | 哪些 ASCII 字形必须保留（`rebuild_fonts.py --ascii-keep`）|
| `check_metrics.py` | 检查字宽、行高、间距是否对齐 |
| `set_bfloor.py` | 改链接脚本里的 B 区余量下限（空间紧时调）|
| `keep_cjk.txt` | 原厂字体本来就有的汉字（不占空间）——本版为空：原厂 TEXT22 没有汉字，全部自绘 |
| `need_glyphs.txt` | 需要自己画的字形（每个汉字约 40 字节）|

字形的来龙去脉见 [开发记录](../docs/开发记录.md)，空间账见 [README「闪存余量」](../README.md#闪存余量很紧)。
