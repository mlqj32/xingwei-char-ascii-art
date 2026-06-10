# -*- coding: utf-8 -*-
"""生成 docs/alignment_status.json — 追踪完全对齐进度。"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYMBOLS = ROOT / "docs" / "charart_symbols.txt"

# 内联辅助 code object：已由父函数/run_gui 覆盖，不计入待还原
INLINE_COVERED = frozenset({
    "<genexpr>", "<lambda>", "worker", "worker_static", "apply_on_main",
    "on_close", "do_del", "tag_for",
})

MODULE_RECOVERED = {
    "_escape_c_string": "charart_core.py",
    "art_to_code": "charart_core.py",
    "_t": "charart_i18n.py",
    "_rgba_frames_to_gif_p": "charart_core.py",
    "_render_art_to_image": "charart_core.py",
    "_apply_effect": "charart_core.py",
    "_charart_from_pil": "charart_core.py",
    "generate_charart": "charart_core.py",
    "get_animated_frames": "charart_core.py",
    "main": "charart.py",
}

CONFIG_RECOVERED = {
    "load_recent_paths": "charart_gui.py",
    "save_recent_paths": "charart_gui.py",
    "load_presets_dict": "charart_gui.py",
    "save_presets_dict": "charart_gui.py",
    "load_last_path": "charart_gui.py",
    "save_last_path": "charart_gui.py",
}

DISPLAY_RECOVERED = {
    "_pad_to_display_static": "charart_display.py",
    "pad_to_display": "charart_display.py",
    "stop_animation": "charart_display.py",
}

EXPORT_RECOVERED = {
    "get_art_text": "charart_export.py",
    "get_art_html": "charart_export.py",
    "copy_art": "charart_export.py",
    "export_txt": "charart_export.py",
    "export_html": "charart_export.py",
    "export_png": "charart_export.py",
    "export_gif": "charart_export.py",
}

PRESET_RECOVERED = {
    "save_current_preset": "charart_presets.py",
    "load_preset_by_name": "charart_presets.py",
    "refresh_preset_menu": "charart_presets.py",
    "delete_preset": "charart_gui_misc.py",
}

DND_RECOVERED = {
    "show_drop_overlay": "charart_dnd.py",
    "hide_drop_overlay": "charart_dnd.py",
    "on_drop_art": "charart_dnd.py",
    "on_drop_enter_art": "charart_dnd.py",
    "on_drop_leave_art": "charart_dnd.py",
    "on_drop_root": "charart_dnd.py",
    "on_drop_windnd": "charart_dnd.py",
}

SHOW_RECOVERED = {
    "show_code": "charart_show.py",
    "show_padded": "charart_show.py",
    "play_next_frame": "charart_show.py",
}

PREVIEW_RECOVERED = {
    "load_preview_photo": "charart_preview.py",
    "_pil_to_photo": "charart_preview.py",
    "_stop_preview_gif": "charart_preview.py",
    "_preview_gif_next": "charart_preview.py",
    "update_preview_window": "charart_preview.py",
    "show_original": "charart_preview.py",
}

GUI_LOGIC_RECOVERED = {
    "refresh_art": "charart_gui.refresh_art_logic",
    "open_image": "charart_gui.open_image_logic",
    "get_gui_width": "charart_gui_misc.py",
    "get_gui_height": "charart_gui_misc.py",
    "get_transparent_bg_rgb": "charart_gui_misc.py",
    "refresh_ui_lang": "charart_gui_misc.py",
    "show_progress_determinate": "charart_gui_misc.py",
    "update_progress": "charart_gui_misc.py",
    "show_progress_indeterminate": "charart_gui_misc.py",
    "close_progress": "charart_gui_misc.py",
    "update_foot_and_size": "charart_gui_misc.py",
    "on_size_or_zoom_change": "charart_gui_misc.py",
    "on_style_or_effect_change": "charart_gui_misc.py",
    "batch_export": "charart_gui_misc.py",
    "on_size_preset_change": "charart_run_gui.py (inline)",
    "sync_size_and_refresh": "charart_gui_misc.py",
    "reset_size_default": "charart_gui_misc.py",
    "refresh_recent_menu": "charart_gui_misc.py",
    "open_author_bilibili": "charart_gui_misc.py",
    "on_speed_change": "charart_gui_misc.py",
    "update_scrollbar_visibility": "charart_gui_misc.py",
    "block_insert": "charart_gui_misc.py",
    "block_copy": "charart_gui_misc.py",
    "block_select": "charart_gui_misc.py",
    "close_preview_if_open": "charart_gui_misc.py",
    "on_closing": "charart_gui_misc.py",
    "t": "charart_run_gui.py (closure → charart_i18n._t)",
    "run_gui": "charart_run_gui.run_gui_native",
}

ALL_RECOVERED = {
    **MODULE_RECOVERED,
    **CONFIG_RECOVERED,
    **GUI_LOGIC_RECOVERED,
    **DISPLAY_RECOVERED,
    **EXPORT_RECOVERED,
    **PRESET_RECOVERED,
    **DND_RECOVERED,
    **SHOW_RECOVERED,
    **PREVIEW_RECOVERED,
}


def _parse_symbols() -> list[dict]:
    items = []
    for line in SYMBOLS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(\S+)\s+line~(\d+)", line)
        if m:
            items.append({"name": m.group(1), "line": int(m.group(2))})
    return items


def main() -> None:
    symbols = _parse_symbols()
    named = [s for s in symbols if s["name"] != "<module>"]
    recovered_names = set(ALL_RECOVERED) | INLINE_COVERED

    still = [
        s["name"]
        for s in named
        if s["name"] not in recovered_names
    ]

    total_trackable = len(named) - sum(1 for s in named if s["name"] in INLINE_COVERED)
    recovered_count = len([s for s in named if s["name"] in ALL_RECOVERED])
    pct = round(100 * recovered_count / total_trackable, 1) if total_trackable else 100.0

    status = {
        "target": "完全对齐原版 exe → 单一 charart.py → PyInstaller",
        "progress_percent": pct,
        "recovered_functions": recovered_count,
        "total_code_objects": len(named),
        "inline_covered": sorted(INLINE_COVERED),
        "module_level": MODULE_RECOVERED,
        "config_io": CONFIG_RECOVERED,
        "gui_native": GUI_LOGIC_RECOVERED,
        "recovered_all": ALL_RECOVERED,
        "still_in_pyc": still,
        "still_in_pyc_count": len(still),
        "pyc_dependency": "已移除开发依赖；CHARART_STRICT=1 + charart.pyc 仅作可选对照",
        "default_entry": "charart_run_gui.run_gui_native()",
        "pyinstaller": "charart.spec → dist/星薇字符画.exe（build.bat）",
        "verify": [
            "python tools/parity_check.py",
            "python tools/verify_native.py",
            "run-dev.bat",
            "run-strict.bat",
            "build.bat",
        ],
        "next_priority": [
            "手工 GUI 回归（dev vs strict 若有 pyc）",
            "build.bat → dist/星薇字符画.exe",
        ],
    }

    out = ROOT / "docs" / "alignment_status.json"
    out.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out} — {pct}% ({recovered_count}/{total_trackable}) still={len(still)}")


if __name__ == "__main__":
    main()
