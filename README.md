# 星薇字符画 · Xingwei Char ASCII Art

将图片（含透明通道）转为等比例字符画，支持 PNG / JPG / BMP / GIF / WebP 等格式。  
带图形界面、彩色模式、动图播放、多格式导出、预设与多语言。

English: Turn images into proportional ASCII / character art with a Tkinter GUI, animated GIF support, color mode, and export to TXT / HTML / PNG / GIF.

---

## 功能特性

- 打开或拖拽图片，实时生成字符画
- 多种字符样式（默认、方块、细线等）与效果（正常 / 反相 / 高对比）
- **彩色模式**：按像素颜色渲染字符
- **动图 GIF**：多帧播放、速度调节
- **代码风格**：可显示为 C / Java / Python 等代码形式
- 导出 TXT、HTML、PNG、GIF；支持批量导出
- 尺寸预设、缩放、透明背景选项
- 最近文件、参数预设、中/繁/英/日界面

## 快速开始

### 方式一：从源码运行

需要 **Python 3.13+** 与 **Windows**（拖拽推荐 tkinterdnd2）。

```bat
run-dev.bat
```

或：

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### 方式二：打包为 Windows exe

```bat
build.bat
```

产物：`dist\星薇字符画.exe`（单文件，约 32 MB，无控制台窗口）。

### 命令行预览（可选）

```bat
python charart.py --cli
```

将示例图片放在程序目录，文件名为 `萝薇日常.png`。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开图片 |
| `Ctrl+C` | 复制（HTML 富文本） |
| `Ctrl+S` | 导出 TXT |
| `Ctrl+H` | 导出 HTML |
| `Esc` | 关闭原图预览 |

## 项目结构

```
├── charart.py              # 统一入口（GUI / CLI）
├── charart_run_gui.py      # GUI 主界面
├── charart_core.py         # 字符画生成算法
├── charart_gui.py          # 刷新、打开图片、配置读写
├── charart_show.py         # 画布显示与动图帧
├── charart_export.py       # 导出与复制
├── charart_preview.py      # 原图预览
├── charart_i18n.py         # 多语言与常量
├── run.py / run-dev.bat    # 启动脚本
├── build.bat / charart.spec # PyInstaller 打包
├── requirements.txt
├── tools/
│   ├── parity_check.py     # 核心算法自检
│   └── verify_native.py    # 模块导入冒烟测试
└── docs/
    └── module_constants.json  # 界面文案
```

## 配置与数据文件

运行时会在 **exe 同目录** 或 **源码目录** 生成：

| 文件 | 说明 |
|------|------|
| `.charart_recent` | 最近打开的路径 |
| `.charart_last_path` | 上次打开的图片 |
| `.charart_presets.json` | 用户预设 |

## 开发

```bat
python tools\verify_native.py
python tools\parity_check.py
```

## 依赖

- [Pillow](https://python-pillow.org/) — 图像读写
- [tkinterdnd2](https://pypi.org/project/tkinterdnd2/) — 拖拽（优先）
- [windnd](https://pypi.org/project/windnd/) — Windows 拖拽回退
- [pywin32](https://pypi.org/project/pywin32/) — 剪贴板 HTML 复制

## 作者

- B 站：[space.bilibili.com/259516939](https://space.bilibili.com/259516939)
- Steam《萝薇日记》：[store.steampowered.com/app/4448620](https://store.steampowered.com/app/4448620/_/)

## License

MIT © 星薇Star
