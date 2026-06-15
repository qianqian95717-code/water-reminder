# 💧 Water Reminder · 喝水提醒小工具

> 一个强迫你按时喝水的 Windows 桌面小工具 —— 不喝水它会越来越大，直到占满你的整个屏幕！

---

## ✨ 功能特性

- 🕐 每隔 **1小时** 自动从屏幕左上角弹出可爱水杯
- 🌊 水杯带有浮动动效，萌萌的
- 📈 若不点击喝水，每 **5秒** 窗口自动变大一圈
- 😱 铺满屏幕后显示 **"当前屏幕已被霸占，请立即喝水！"**
- ✅ 点击「我喝了！」后窗口淡出消失，1小时后再次提醒

---

## 🖥️ 效果预览

| 初始弹出 | 逐渐变大 | 全屏霸占 |
|---|---|---|
| 左上角小水杯 | 水杯越来越大 | 蓝色全屏警告 |

---

## 🚀 使用方法

### 方法一：直接运行源码（需要 Python）

1. 确保已安装 Python 3.x（[下载地址](https://www.python.org/downloads/)）
2. 下载 `water_reminder.py`
3. 在终端运行：

```bash
python water_reminder.py
```

### 方法二：下载 .exe 直接运行（无需 Python）

1. 在 [Releases](../../releases) 页面下载最新的 `water_reminder.exe`
2. 双击运行即可

---

## ⚙️ 自定义配置

打开 `water_reminder.py`，修改顶部的参数：

```python
REMIND_INTERVAL = 60 * 60   # 提醒间隔（秒），默认1小时
GROW_INTERVAL   = 5         # 多少秒变大一次
GROW_STEP       = 0.08      # 每次变大幅度（0.08 = 屏幕宽度的8%）
INIT_FRAC       = 0.20      # 初始窗口大小（屏幕宽度的20%）
```

---

## 📦 自行打包为 .exe

如需自行打包，在 Windows 上执行：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name water_reminder water_reminder.py
```

打包完成后 `.exe` 文件在 `dist/` 目录下。

---

## 📁 项目结构

```
water-reminder/
├── water_reminder.py     # 源代码
├── water_reminder.exe    # 打包后的可执行文件（Windows）
└── README.md             # 说明文档
```

---

## 📄 License

MIT License · 随便用，随便改 😄
