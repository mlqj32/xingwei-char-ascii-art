# -*- mode: python ; coding: utf-8 -*-
# PyInstaller 重打包（纯 Python 工程，不依赖 charart.pyc）
# 用法: build.bat  或  pyinstaller charart.spec

import sys
from pathlib import Path

root = Path(SPECPATH)

# 可选资源：图标 / 示例图
_datas = [(str(root / "docs" / "module_constants.json"), "docs")]
for name in ("icon.png", "icon.ico", "图标.png", "图标.ico", "萝薇日常.png"):
    p = root / name
    if p.is_file():
        _datas.append((str(p), "."))

_hidden = [
    "charart_core",
    "charart_i18n",
    "charart_display",
    "charart_export",
    "charart_presets",
    "charart_dnd",
    "charart_show",
    "charart_preview",
    "charart_gui",
    "charart_gui_misc",
    "charart_run_gui",
    "PIL._tkinter_finder",
    "tkinterdnd2",
    "windnd",
    "win32clipboard",
    "win32api",
]

# tkinterdnd2 的 Tcl 扩展
try:
    from PyInstaller.utils.hooks import collect_data_files, collect_submodules

    _datas += collect_data_files("tkinterdnd2")
    _hidden += collect_submodules("tkinterdnd2")
except Exception:
    pass

_icon = None
for name in ("icon.ico", "图标.ico", "icon.png", "图标.png"):
    p = root / name
    if p.is_file():
        _icon = str(p)
        break

a = Analysis(
    [str(root / "charart.py")],
    pathex=[str(root)],
    binaries=[],
    datas=_datas,
    hiddenimports=_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["charart_hooks"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="星薇字符画",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
