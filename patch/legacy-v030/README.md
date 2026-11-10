# legacy-v030/ —— v0.3.0 汉化的历史留档

本目录是**历史**，不是当前流水线的一部分。里面的 115 个文件是 v0.3.0 汉化过程中
一步步打出来的锚点补丁和一次性诊断脚本：每加一批译文或修一处布局，就新写一个脚本，
按 `mkpatch2.py` … `mkpatch35_cross.py` 的顺序叠上去。

## 用之前先看这三条

- **只对 v0.3.0 的源码有效**。里面所有锚点（`OLD = "..."`）都取自 v0.3.0 的原始字符串，
  换成 v0.4.x 一个都对不上——不要拿它打当前源码。
- **不要按目录顺序重放到 v0.4.1**。v0.4.1 走的是另一条路：以 `zh_dict.csv` 为唯一
  译文来源，由 [`../v041/apply_dict.py`](../v041/apply_dict.py) 统一套用；
  这些脚本留下的"改一处写一个脚本"的做法已经废弃。
- **留着的理由只有一个**：`../v041/harvest_patches.py` 要从这些脚本里把
  `(旧英文, 新中文)` 成对抽出来，复现 `zh_dict.csv` 里那批译文的来源。
  ```bash
  python3 patch/v041/harvest_patches.py --patch-dir patch/legacy-v030
  ```
  删了这个目录，`zh_dict.csv` 仍然是完整的（它是唯一来源），但"这条译文当初是怎么定的"
  就查不到了。

## 大致分类

| 类别 | 代表文件 |
|---|---|
| 逐批汉化的锚点补丁（主序列） | `mkpatch2.py` … `mkpatch35_cross.py` |
| 示波器页 | `mka2.py`、`mka22.py`、`mkwave.py`、`scope_tabs.py`、`scope_popup2.py`、`trig_popup.py`、`trig_label.py`、`widen_filter.py`、`smooth_*.py`、`flicker*.py`、`noflicker2.py` |
| 图库 | `gal_*.py`、`cross_page_delete.py`、`clip_rows.py`、`trim_rows.py` |
| 记录 / 帮助 / 信息页 | `mkhelp.py`、`fix_rec.py`、`rec_hunt.py`、`fix_inf.py`、`drop_help.py` |
| 电源、充电、关机 | `fix_charging*.py`、`patch_charge*.py`、`patch_off.py`、`pullup.py`、`reuse_rest.py`、`ir_drop.py` |
| 链接脚本与空间 | `mklink.py`、`fix_link*.py`、`rebalance.py` |
| 崩溃/异常诊断 | `diag_panic.py`、`panic_hunt.py`、`undo_diag.py`、`repair.py`、`detect_by_jump.py`、`absolute_thr*.py` |
| 排版、滚动、按钮 | `scroll_*.py`、`smooth_app*.py`、`six_rows.py`、`measure_row.py`、`type_row.py`、`label_yfix.py`、`nav_buttons2.py`、`meas_btn.py` |
| v0.3.0 的构建脚本 | `build_zh.sh`、`test_zh.sh`——路径写死在 `F:/desk/study/dm40`，当前机器上已不可用，v0.4.1 用 [`../v041/build_zh.sh`](../v041/build_zh.sh) |
| v0.3.0 的笔记 | `SCOPE.md`（示波器功能逆向笔记）、`splash_anim.rs`（早期开机动画实验，未采用） |

## 现在该看哪里

- 刷机与校验值：仓库根 [`README.md`](../../README.md)
- 当前流水线与各脚本作用：[`../v041/README.md`](../v041/README.md)、[`../README.md`](../README.md)
- 字形/字库工具（`derive_sets.py`、`rebuild_fonts.py`、`gen_splash_img2.py` 等）
  在上一级 [`patch/`](../) 里，不在本目录
- 当时的开发笔记：[`docs/开发记录.md`](../../docs/开发记录.md)
