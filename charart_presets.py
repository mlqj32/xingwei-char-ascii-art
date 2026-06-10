# -*- coding: utf-8 -*-
"""预设读写与菜单（对照 charart.py line 1420-1747）。"""
from __future__ import annotations

from typing import Callable


def save_current_preset_logic(
    *,
    simpledialog_askstring: Callable[..., str | None],
    root,
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    current_style_get: Callable[[], str],
    current_effect_get: Callable[[], str],
    color_mode_get: Callable[[], bool],
    transparent_get: Callable[[], str],
    zoom_get: Callable[[], int],
    presets_dict: dict,
    save_presets_dict: Callable[[dict], None],
    refresh_preset_menu: Callable[[], None],
    refresh_ui_lang: Callable[[], None],
    messagebox_showinfo: Callable[[str, str], None],
    t: Callable[[str], str],
) -> None:
    """line 1420-1437"""
    name = simpledialog_askstring(
        t("dialog_save_preset"),
        t("preset_name_prompt"),
        parent=root,
    )
    if not name or not name.strip():
        return
    key = name.strip()
    presets_dict[key] = {
        "width": get_gui_width(),
        "height": get_gui_height(),
        "style": current_style_get(),
        "effect": current_effect_get(),
        "color_mode": color_mode_get(),
        "transparent": transparent_get(),
        "zoom": zoom_get(),
    }
    save_presets_dict(presets_dict)
    refresh_preset_menu()
    refresh_ui_lang()
    messagebox_showinfo(t("lbl_preset"), t("msg_preset_saved") % key)


def load_preset_by_name_logic(
    *,
    name: str,
    presets_dict: dict,
    width_var_set: Callable[[int], None],
    height_var_set: Callable[[int], None],
    current_style_set: Callable[[str], None],
    current_effect_set: Callable[[str], None],
    color_mode_set: Callable[[bool], None],
    transparent_set: Callable[[str], None],
    zoom_set: Callable[[int], None],
    on_size_or_zoom_change: Callable[[], None],
) -> None:
    """line 1439-1452"""
    p = presets_dict.get(name)
    if not p:
        return
    width_var_set(max(8, min(200, int(p.get("width", 68)))))
    height_var_set(max(6, min(120, int(p.get("height", 40)))))
    current_style_set(p.get("style", "默认"))
    current_effect_set(p.get("effect", "正常"))
    color_mode_set(bool(p.get("color_mode", False)))
    transparent_set(p.get("transparent", "透明"))
    zoom_set(max(8, min(16, int(p.get("zoom", 9)))))
    on_size_or_zoom_change()


def refresh_preset_menu_logic(
    *,
    preset_menu,
    tk_end,
    presets_dict: dict,
    t: Callable[[str], str],
    save_current_preset: Callable[[], None],
    load_preset_by_name: Callable[[str], None],
    delete_preset: Callable[[], None],
) -> None:
    """line 1740-1747"""
    preset_menu.delete(0, tk_end)
    preset_menu.add_command(label=t("preset_save"), command=save_current_preset)
    preset_menu.add_separator()
    for name in presets_dict:
        preset_menu.add_command(
            label=name,
            command=lambda n=name: load_preset_by_name(n),
        )
    preset_menu.add_separator()
    preset_menu.add_command(label=t("preset_delete"), command=delete_preset)
