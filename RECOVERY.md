# Star 薇字符画 — 工程恢复说明

## 项目类型

- **原始发布**：PyInstaller 单文件 exe（Python 3.13）
- **主逻辑文件**：`charart.py` → 打包为 `charart.pyc`（约 2000 行 GUI + 字符画算法）

## 恢复结果

| 内容 | 状态 |
|------|------|
| 可运行字节码 `charart.pyc` | ✅ 已提取 |
| 完整 Python 源码 `.py` | ✅ **100% 还原**（`charart_run_gui.py` + 各模块；`tools/alignment_status.py` 报告 100%） |
| 函数符号表 | ✅ `docs/charart_symbols.txt`（101 个 code object） |
| 字节码反汇编 | ✅ `docs/charart_disassembly.txt` |
| 部分函数片段 | ✅ `docs/charart_recovered.py`（约 7/101 成功） |
| 图标资源 | ✅ `icon.png` |

## 本地运行（开发）

```bat
run-dev.bat
```

无需 `charart.pyc`。严格对照原版（需保留 pyc）：

```bat
run-strict.bat
```

## 打包 exe

```bat
build.bat
```

输出：`dist\星薇字符画.exe`

## 依赖

- Python **3.13**（与 exe 一致）
- Pillow、PyYAML、NumPy、tkinterdnd2、windnd、pywin32

## 修改代码

当前可直接运行 `charart.pyc`。若要改源码，可：

1. 参考 `docs/charart_disassembly.txt` 对照修改
2. 运行 `python tools/parity_check.py` 确认与 pyc 行为一致
3. 完全对齐路线图见 [ALIGNMENT.md](ALIGNMENT.md)
4. 严格模式（等同 exe）：`run-strict.bat` 或 `set CHARART_STRICT=1`

## 技术栈（从 exe 分析）

- **GUI**：Tkinter + tkinterdnd2 + windnd（拖拽）
- **图像**：Pillow
- **配置**：PyYAML / JSON 预设
- **数值**：NumPy
