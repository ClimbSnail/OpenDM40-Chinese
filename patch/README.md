# patch/ —— 改动脚本说明

这里的脚本**不是**给使用者用的，是记录“从 opendm40 原版到中文版”做了哪些改动。
想自己重建中文固件，看 [README 的「从源码重建」](../README.md#从源码重建)。

## 两代做法

| 阶段 | 做法 | 说明 |
|---|---|---|
| v0.3.0（zh1~zh8）| **文本锚点替换** | 一个改动一个 `mkpatchNN.py`，读源文件、断言锚点唯一、替换、写回 |
| v0.4.0（zh9 起）| **翻译字典移植** | 上游改了约 5000 行，锚点全废。改为：从旧补丁里抽出 147 条纯文案对照，套到新源码；剩下的逐条翻译 |

所以 `mkpatchNN.py` 这些只对 v0.3.0 有意义；v0.4.0 的改动见下一节。

所有脚本都是**文本替换**：读源文件、断言锚点唯一、替换、写回。
锚点不唯一就直接报错退出，所以脚本要么完整生效、要么什么都不改。

---

## 一、构建链（必需，缺了编不出来）

| 文件 | 作用 |
|---|---|
| `build_zh.sh` | 构建入口。设置 PATH、进源码目录、`cargo build`，打印各区域剩余字节 |
| `derive_sets.py` | 扫描源码里的字符串字面量，产出下面两个字形清单 |
| `rebuild_fonts.py` | 按清单重新生成 `stockfont_data.rs`（只保留用到的字形）|
| `set_bfloor.py` | 改链接脚本里的 B 区余量下限（空间紧时调）|
| `check_metrics.py` | 检查字宽、行高、间距是否对齐 |
| `test_zh.sh` | 快速自检 |
| `ascii_keep.py` / `ascii_keep.txt` | 哪些 ASCII 字形必须保留 |
| `keep_cjk.txt` | 用原厂字体就有的汉字（不占空间）|
| `need_glyphs.txt` | 需要自己画的汉字（每个约 64 字节）|

## 二、主序列：`mkpatch2.py` ~ `mkpatch35_cross.py`

按编号顺序从原版源码开始应用，覆盖了绝大部分汉化和功能改动：

| 编号 | 内容 |
|---|---|
| 2 ~ 8 | 第一批汉化：主菜单、设置页、量程、温度、限值、记录、信号源 |
| 9 ~ 23 | 弹窗改用 TEXT22、暗屏档位、蜂鸣音调、示波器页签、帮助页删减 |
| 24 | 大改动：多处文案与布局 |
| 25 ~ 34 | 设置页单页滚动、图库、涌浪页、示波器全中文 |
| 35_cross | 图库跨页勾选 |

**重建时按编号顺序跑**，中途断链会失败。

## 三、单项修复（按功能索引）

| 功能 | 脚本 |
|---|---|
| 设置页闪屏 | `flicker.py`、`flicker2.py`、`noflicker2.py` |
| 设置页行数/裁剪 | `six_rows.py`、`trim_rows.py`、`clip_rows.py`、`scroll_ui.py`、`scroll_app.py`、`scroll_app2.py` |
| 跟手滑动（**已回退**）| `smooth_ui.py`、`smooth_app.py`、`smooth_fix2.py` |
| 图库 | `gal_*.py`（8 个）、`cross_page_delete.py` |
| 示波器 | `scope_tabs.py`、`scope_popup2.py`、`trig_label.py`、`trig_popup.py`、`type_row.py`、`meas_btn.py`、`measure_row.py` |
| 涌流页 | `inrush_zh.py` |
| 触摸测试 | `tt_zh.py` |
| 报警提示 | `alert_zh.py`、`dlg_zh.py`、`wiring_zh.py` |
| 接线弹窗 | `wiring_zh.py`、`mkwave.py` |
| 刷新/时序 | `refresh_fix3.py`、`title_once.py`、`swipe_u.py`、`undo_view_fix.py` |
| 链接/字形表 | `mklink.py`、`fix_link.py`、`fix_link2.py`、`mka2.py`、`mka22.py`、`rebalance.py` |
| 崩溃排查 | `panic_hunt.py`、`rec_hunt.py`、`diag_panic.py`、`undo_diag.py`、`repair.py`、`fix_rec.py`、`fix_inf.py` |
| 其它 | `mode_fix.py`、`label_yfix.py`、`nav_buttons2.py`、`mkhelp.py` |

## 四、开机画面

| 文件 | 状态 |
|---|---|
| `gen_splash_img2.py` | 生成位图模块 `splash_img.rs` 的脚本 |
| `splash_img.rs` | **生效中**：208×51 单色位图 + 绘制循环，放 A2 区 |
| `splash_anim.rs` | **已废弃**：扫描动画版本，改成图片后不再使用 |
| `add_anim.py` | 已废弃：当初把动画挂进启动流程的脚本 |

## 五、充电指示（试了三轮，留档）

最终生效的是**最后两个**，其余是过程记录：

| 脚本 | 做法 | 结果 |
|---|---|---|
| `patch_charge.py` / `patch_charge2.py` | 充电时电池整格变绿 + 闪 | 颜色太扎眼 |
| `soft_green.py` | 改柔和绿 + 明暗呼吸 | 呼吸被否掉 |
| `cell_blink.py` | 恢复单格闪 | 保留 |
| `outline_white.py` / `outline_white2.py` | 外框白、格子绿（paint+clip）| **采用** |
| `pullup.py` | 给充电芯片状态脚加上拉 | 引脚读不出变化，没用 |
| `detect_by_jump.py` | 按电压跳变判定 | 纹波导致状态卡死 |
| `absolute_thr.py` / `absolute_thr2.py` | 按电压绝对值判定 | 只在快充满时有效 |
| `ir_drop.py` | **按内阻压降判定** | **采用** |
| `blink_next.py` | 闪“正在充进去的下一格” | **采用** |
| `show_mv.py` | 临时把电压画到屏幕上（调试用）| 用完已撤 |

结论和三次失败的原因写在 [CHANGELOG](../CHANGELOG.md)。

## 六、其它

| 文件 | 说明 |
|---|---|
| `stockfont_data.rs` | 重新生成后的字体数据（214 KB），构建时直接替换源码里同名文件 |
| `Widen_filter.py`（实际名 `widen_filter.py`）| 放宽字形筛选，把全角标点 `？，：…` 也纳入 |
| `SCOPE.md` | 示波器相关的逆向笔记 |

---

## 四、v0.4.0 / zh10 的改动脚本（放在 `4-工具/`，未收进本目录）

这些是 2026-11-08 那一轮逐屏精修用的脚本，都是幂等的文本替换，保留下来备查：

| 脚本 | 作用 |
|---|---|
| `zh_device_help.py` | 设备信息页五项 + 帮助页第二项 |
| `zh_limits.py` | 限值页标题（按 UTF-8 字节写缓冲）、ON→开、Upper/Lower |
| `zh_meas.py` / `meas_text22.py` | 示波器 20 个测量项改中文，并把绘制字体换成 TEXT22 |
| `scope_tabs.py` | 示波器弹窗 33 行 `SC_F16` → `TEXT22`，附带补译 |
| `zh_scope2.py` 等 | 触发/解码页文案 |
| `auto_en.py` | 档位标签改回 `AUTO / AUTO+`，运行状态改回 `RUN` |
| `doc_scope.py` / `doc_scope2.py` / `doc_head_set.py` / `doc_dev_font.py` | 同步更新说明书与开发记录 |

> 注意：`--font SC_F16:...` 这条路**走不通**（渲染乱码），细节见
> [开发记录 · 字体](../docs/开发记录.md#字体汉字只能靠-text222026-11-08-定论)。
