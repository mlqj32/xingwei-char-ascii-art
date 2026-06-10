# -*- coding: utf-8 -*-
"""Bootstrap launcher for recovered Star CharArt project."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    strict = os.environ.get("CHARART_STRICT", "").strip() in ("1", "true", "yes")

    sys.path.insert(0, str(ROOT))
    venv_site = ROOT / ".venv" / "Lib" / "site-packages"
    if venv_site.is_dir():
        sys.path.insert(0, str(venv_site))

    if strict:
        from charart_gui import run_gui as _run_gui

        _run_gui(strict=True)
        return

    if (ROOT / "charart.py").is_file():
        from charart import main as charart_main
        charart_main()
        return

    if (ROOT / "charart_gui.py").is_file():
        from charart_gui import run_gui
        run_gui()
        return

    print("[ERROR] 未找到 charart 入口")


if __name__ == "__main__":
    main()
