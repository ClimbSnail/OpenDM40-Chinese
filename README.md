# OpenDM40-Chinese

[opendm40](https://github.com/opendm40/opendm40) 开源万用表固件的**简体中文汉化**，
面向正点原子 **DM40A / DM40B / DM40C**，基于 **v0.3.0** 源码。

已在 **DM40A 真机**上测试通过。

> opendm40 官方只有英文界面。本项目把主菜单、设置页、量程页等改为中文，
> 并提供一份完整的中文使用说明书。

---

## 效果

| 主菜单 | 设置 1/3 |
|---|---|
| ![主菜单](screenshots/主菜单.png) | ![设置1](screenshots/设置1.png) |

| 设置 2/3 | 设置 3/3 |
|---|---|
| ![设置2](screenshots/设置2.png) | ![设置3](screenshots/设置3.png) |

| 量程页 | 测量页 |
|---|---|
| ![量程页](screenshots/量程页.png) | ![测量页](screenshots/测量页.png) |

---

## 汉化范围

### 已中文

- **主菜单**全部 6 项：图库 截图记录 / 万用表 / 示波器 / 信号源 / 设置 /
  组合视图 万用表+示波器
- **设置三页**：26 个行标签 + 全部选项值
  （暗屏时间 5分 / 电源方式 自动 (按视图) / 显示行 柱状图 / U盘 只读 …）
- **量程页**：电压设置 / 自动+ 更安全：不降到 mV / 保持限值 / 波形 / 确定 /
  保险丝自检 / 涌流
- **各页标题**：设置 / 量程 / 键盘 / 设备 / 记录 / 图库 / 帮助 / 涌流 / 触摸测试

### 仍为英文（有意保留）

| 位置 | 内容 | 原因 |
|---|---|---|
| 测量页小标签 | `MAX` `AVG` `MIN` `REL` `320ms/div` `MED 5.0/s` | 该处用 F14 字体（14 px / 1 bpp），行距仅 12 px。中文在 14 px 放不下，降到 11 px 后笔画糊成一团（见 `screenshots/时间基准-11px失败样例.png`） |
| 状态栏 | `AUTO+` `RUN` `HOLD` | 该处用 F21 字体（21 px **4 bpp**），约 110 字节/字，且属通用符号 |
| 单位与标准缩写 | `60mV` `6V` `AUTO+` `DC/AC/AC+DC` | 本身就是符号 |
| 帮助页正文 | 4 页英文说明 | 见下 |

**帮助页从 7 页减为 4 页**（保留：手势 / 侧键 / 万用表 / 限值），
为字形腾出约 1 KB 闪存。第 4 页「限值」保留是因为它含
`OUT 插孔绝不要接电压源` —— 全书唯一的安全警告。

---

## 刷机教程

> ⚠️ **实测结论**：在 v0.3.0 上，
> ①「把升级文件拷进 U 盘等表弹窗」和 ②「关机时长按电源键进加载器」
> **这两条官方途径都不工作**。只能用 USB SCPI。

### 1. 准备 USB 驱动

Windows 自带没有 USBTMC 驱动，设备管理器里该设备显示为「其他设备 · 代码 28」。

1. 下载 [Zadig](https://zadig.akeo.ie/)
2. **以管理员身份运行** → `Options` → `List All Devices`
3. 下拉列表里找到 **`DM40 multimeter (opendm40)`**，会显示两个条目：
   - **`(Interface 0)`** ← **选这个**（仪器接口）
   - `(Interface 1)` ← 不要选，那是大容量存储
4. 目标驱动选 **`WinUSB`** → `Install Driver`

### 2. 准备 Python 环境

```bash
pip install pyvisa pyvisa-py pyusb libusb-package
```

### 3. 刷入

表通过 USB 连上电脑，运行：

```bash
python tools/upload_zh.py firmware/opendm40-v0.3.0-zh.bin --update --wait 120
```

它会：

1. `DBG:UPLOAD:BEGIN <len>,<crc32>`
2. 分块 `DBG:UPLOAD:DATA <offset>,<232 字节>` 传 634 KB，约 9 秒
3. `DBG:UPLOAD:END?` —— **表自己重新读取文件并校验 CRC-32**
4. `DBG:UPDATE` —— 清零加载器标记并复位，原厂加载器安装固件

设备会掉出 USB 约 1 秒，随后出现即为新固件。

### 4. 验证

```bash
python tools/dm.py --query 'DBG:BOOT?'
```

返回的加载器标记应与镜像头部一致（本项目为 `0xA0F25F0D 0x0009ADF4 0x000109A2`）。

也可以插上 USB，检查 `INFO/FIRMWARE.BIN` 的 SHA-256 是否等于所刷镜像。

### 5. 截屏（可选）

```bash
python tools/shot.py out.png
```

---

## 回退

用同样的工具，换镜像即可：

```bash
# 回官方英文版
python tools/upload_zh.py firmware/opendm40-v0.3.0-official.bin --update --wait 120

# 回正点原子原厂固件（有中文界面）
python tools/upload_zh.py firmware/dm40_v_2_6-stock.bin --update --wait 120
```

**刷固件从不改动标定区**（`0x080C0000`），所以回退后测量精度不变。

> 无论如何，**装好 opendm40 后第一件事是把 U 盘里的 `INFO/` 整个拷走**。
> 里面的 `CALIB.BIN`、`BOOTDATA.BIN`、`UID.BIN` 是这台表独有、**无法重建**的。

---

## 目录

```
firmware/     三个镜像：中文版、官方英文版、原厂 V2.6
docs/         中文使用说明书（21 章 + 中英对照表）、刷机与构建记录
patch/        从官方源码生成中文版的全部脚本
tools/        USB 刷机 / 截屏 / 导航工具
screenshots/  各界面实拍
```

### patch/ 说明

按顺序作用在 **opendm40 v0.3.0 原始源码**上：

| 脚本 | 作用 |
|---|---|
| `mkpatch2.py` | 设置页标签 + 主菜单 + `view_name` |
| `mkpatch4.py` | 设置页的值（`app.rs` / `meter.rs` / `scope_ui.rs` / `scope_page.rs`） |
| `mkpatch5.py` | 危险警报值 + 采样率显示名 |
| `mkpatch6.py` | 量程页标题 + 保持限值 |
| `mkpatch7.py` | 帮助页 7 → 4 页（腾闪存） |
| `mkpatch8.py` | `Wave` / `OK` / U盘值 / AUTO+ 提示行 |
| `derive_sets.py` | 从七个源文件的字符串字面量反推所需汉字 |
| `rebuild_fonts.py` | 按两种字体的各自编码约定重建 `TEXT22` / `F14` |

`mkpatch3.py` 是记录 F14 汉化失败经过的空操作，保留作说明。

---

## 从源码重建

需要 Rust 工具链（`thumbv7em-none-eabihf` + `llvm-tools`）与 git-bash。
Windows 上的几个坑（`RUSTUP_HOME` 要用 Windows 路径、`PATH` 要用 MSYS 路径、
`stackdepth.py` 缺 `.exe` 后缀）见 `docs/刷机与构建记录.md`。

```bash
git clone --depth 1 --branch v0.3.0 https://github.com/opendm40/opendm40.git
cd opendm40
python3 ../patch/mkpatch2.py firmware/src ...
# …… 按上表顺序应用 mkpatch4 ~ mkpatch8
python3 ../patch/derive_sets.py <vendor-cjk-set> firmware/src/*.rs
python3 ../patch/rebuild_fonts.py --pristine ... --out firmware/src/stockfont_data.rs ...
firmware/build.sh
```

### 闪存余量（很紧）

| 区域 | 剩余 | 硬性下限 |
|---|---|---|
| B（零等待） | 8,476 字节 | 8,192 |
| C | 4,124 字节 | 4,096 |

22 px 汉字约 **60 字节/字**（50 字节位图 + 10 字节条目）。
想再增加中文，必须先腾出空间——这是本项目最大的约束。

---

## 字形是怎么来的

| 来源 | 数量 | 说明 |
|---|---|---|
| 原厂 V2.6 固件自带 | 64 个 | opendm40 已内嵌原厂位图字体，其中 `TEXT22` 含 216 个汉字，按字符串实际用字裁剪到 64 个 |
| 宋体渲染补齐 | 69 个 | 原厂字集没有的字，用宋体 22 px 二值化后按原厂格式编码 |

两者在仪表上字高、字重、基线已一致（见 `screenshots/字形对比-3倍放大.png`）。

> **字形渲染注意**：宋体 22 px 的墨迹是 20 行，基线压在画布底边会把最后 2 行裁掉。
> 正确做法是在放大画布上渲染、取墨迹包围盒后再贴进格子——第一版没这么做，
> 结果字偏小、底部被遮挡。详见 `patch/SCOPE.md`。

---

## 许可与来源

- **代码**：沿用上游 opendm40 的 **MIT**，见 [LICENSE](LICENSE)
- **上游项目**：[opendm40/opendm40](https://github.com/opendm40/opendm40)，MIT
- **中文字形**：64 个来自正点原子 DM40 V2.6 原厂固件的位图字体；
  69 个由宋体（SimSun）渲染得到
- `firmware/dm40_v_2_6-stock.bin` 是**正点原子官方固件，版权归其所有**，
  仅为方便回退而附带
- 本项目与正点原子（Alientek）无关，未获其授权或认可

> ⚠️ 如果你的用途对字体授权敏感（例如商业分发），建议把 69 个手绘字形
> 改用 OFL 授权的开源字体（如 Noto Sans SC / 思源黑体）重新渲染后重编。

---

## 免责声明

刷第三方固件**可能失去原厂保修**，也存在变砖风险。opendm40 的设计
（不动 bootloader、不动标定区、升级失败停在加载器）把风险压到很低，
但**请自行承担后果**，并务必先备份 `INFO/`。

opendm40 上游标注其状态为 **Experimental**：只在一台 DM40A 上实测，
DM40B / DM40C 仅在模拟器验证。涉及 A 插孔通电流的功能未上真机。
