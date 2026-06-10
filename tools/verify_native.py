# -*- coding: utf-8 -*-
"""验证纯 Python 工程可导入且关键入口可用（无需 GUI 交互）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    errors: list[str] = []

    modules = [
        "charart",
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
    ]
    for name in modules:
        try:
            __import__(name)
            print(f"  OK import {name}")
        except Exception as e:
            errors.append(f"import {name}: {e}")
            print(f"  FAIL import {name}: {e}")

    from charart_gui_misc import get_gui_width_logic, get_gui_height_logic

    class _Var:
        def __init__(self, v):
            self._v = v

        def get(self):
            return self._v

    w = get_gui_width_logic(width_var_get=_Var(68).get)
    h = get_gui_height_logic(height_var_get=_Var(40).get)
    if w != 68 or h != 40:
        errors.append(f"size logic: w={w} h={h}")
    else:
        print("  OK get_gui_width/height logic")

    from charart_run_gui import HAS_DND, DND_KIND

    print(f"  OK run_gui_native entry, HAS_DND={HAS_DND}, DND_KIND={DND_KIND!r}")

    i18n = ROOT / "docs" / "module_constants.json"
    if not i18n.is_file():
        errors.append("missing docs/module_constants.json")
    else:
        print("  OK module_constants.json")

    if errors:
        print("\nFAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("\n全部通过 — 纯 Python 工程就绪")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
