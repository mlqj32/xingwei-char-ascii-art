# 星薇字符画 — 完全对齐路线图

目标：**行为与原版 exe 100% 一致**，且 **主逻辑逐步迁移为可读 `charart.py` 源码**，最终可脱离 `charart.pyc` 并重新打包 exe。

## 当前进度（约 15% 源码对齐 → **模块级算法已 parity 通过**）

| 类别 | 函数数 | 已还原为 .py | 说明 |
|------|--------|--------------|------|
| 模块级算法 | 11 | **10** | 含 `_render_art_to_image`、`_rgba_frames_to_gif_p`、`art_to_code` 等 |
| 显示/填充 | 3 | 3 | `charart_display.py`（已挂接 stop/pad） |
| I18N/常量 | — | ✅ | `charart_i18n.py` |
| GUI 闭包 | ~90 | 4 挂接 | refresh / open / stop_animation / pad_to_display |
| 入口 | 2 | 1 | `main()` 在 `charart.py`；`run_gui` 仍在 pyc |

运行 `python tools/alignment_status.py` 生成 `docs/alignment_status.json`。  
运行 `python tools/parity_check.py` — **当前全部 OK**。

## 三阶段计划

### 阶段 A — 行为对齐（可验证）

1. 使用严格模式作为基准：`set CHARART_STRICT=1` → `python run.py`
2. 运行回归：`python tools/parity_check.py`
3. 手工清单：打开/拖拽/导出 PNG·GIF·TXT·HTML/批量/预设/多语言/动图播放

### 阶段 B — 逐函数替换 pyc

每还原一个函数：

1. 对照 `docs/charart_disassembly.txt` 写 `.py`
2. `parity_check.py` 或专项测试与 pyc 输出一致
3. 加入 `_patch_core()` 或合并进 `charart.py`
4. 在 `docs/alignment_status.json` 标记 ✅

待还原（模块级，优先）：

- [ ] `_rgba_frames_to_gif_p`
- [ ] `_render_art_to_image`
- [ ] `_t` / `I18N` 加载

待还原（GUI 闭包，工作量大）：

- [ ] `run_gui` 整体（101 个 code object 中约 90 个嵌套函数）
- [ ] 导出、预览、拖拽、预设等

工具选项：

- **手工 + 反汇编**（当前方案，可靠但慢）
- **[ByteCodeLLM](https://github.com/cyberark/ByteCodeLLM)** + 本地 LLM（可批量处理 3.13 pyc）
- 等待 **pycdc** 完整支持 3.13

### 阶段 C — 单文件 `charart.py` + 重打包 exe

1. 各模块已拆分为 `.py`；入口 `charart.py` → `charart_run_gui.run_gui_native()`
2. **不再依赖** `charart.pyc`（`run-dev.bat` 可直接运行）
3. 打包：`build.bat` 或 `pyinstaller charart.spec` → `dist/星薇字符画.exe`
4. 与原版功能回归对比（`run-strict.bat` 需保留 pyc 时可选）

**当前已挂接 run_gui 闭包（30 个，仅 CHARART_STRICT + pyc 模式）**：见 `charart_hooks.HOOK_SPECS`  
**默认 GUI**：`charart_run_gui.run_gui_native()` — 纯 Python，不依赖 pyc  
`refresh_art`, `open_image`, `export_*`, `get_art_*`, `copy_art`, 预设, 拖拽, `pad_to_display`, `stop_animation`

**ByteCodeLLM**：本机未检测到 `pycdc` / `ollama`；若需加速 `run_gui` 整段反编译，请安装后运行 ByteCodeLLM，再与 `charart_hooks` 逐函数合并。

## 运行模式

| 模式 | 命令 | 用途 |
|------|------|------|
| 开发（可改 .py） | `run-dev.bat` 或 `python run.py` | 注入 core + 挂接 refresh/open |
| 严格（= exe） | `set CHARART_STRICT=1` + `python run.py` | 验收基准 |
| 回归 | `python tools/parity_check.py` | 自动对比 pyc vs core |

## 验收标准（完全对齐）

- [ ] `tools/parity_check.py` 全部 OK
- [ ] GUI 功能手工清单 100% 通过（严格模式 vs 开发模式结果一致）
- [ ] 仓库内无 `charart.pyc` 依赖，`charart.py` 可独立运行
- [ ] PyInstaller 重打包 exe 与原版功能等价
