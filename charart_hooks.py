# -*- coding: utf-8 -*-
"""run_gui 闭包函数 → 还原 .py 逻辑的挂接注册表。"""
from __future__ import annotations

import inspect
from typing import Any, Callable

from charart_dnd import (
    hide_drop_overlay_logic,
    on_drop_art_logic,
    on_drop_enter_art_logic,
    on_drop_leave_art_logic,
    on_drop_root_logic,
    on_drop_windnd_logic,
    show_drop_overlay_logic,
)
from charart_display import pad_to_display as pad_to_display_fn
from charart_display import stop_animation_logic
from charart_export import (
    copy_art_logic,
    export_gif_logic,
    export_html_logic,
    export_png_logic,
    export_txt_logic,
    get_art_html_logic,
    get_art_text_logic,
)
from charart_presets import (
    load_preset_by_name_logic,
    refresh_preset_menu_logic,
    save_current_preset_logic,
)
from charart_preview import (
    load_preview_photo_logic,
    pil_to_photo_logic,
    preview_gif_next_logic,
    preview_on_close_logic,
    show_original_logic,
    stop_preview_gif_logic,
    update_preview_window_logic,
)
from charart_show import (
    play_next_frame_logic,
    show_code_logic,
    show_padded_logic,
)

# 由 charart_gui 注入，避免循环 import
refresh_art_logic = None
open_image_logic = None


def _cells(func) -> dict[str, Any]:
    if not getattr(func, "__closure__", None):
        return {}
    return {
        name: cell.cell_contents
        for name, cell in zip(func.__code__.co_freevars, func.__closure__)
    }


def _cell_map(func) -> dict[str, Any]:
    if not getattr(func, "__closure__", None):
        return {}
    return {
        name: cell
        for name, cell in zip(func.__code__.co_freevars, func.__closure__)
    }


def _deref(cm: dict[str, Any], name: str) -> Any:
    return cm[name].cell_contents


def _patched(fn: Callable, name: str) -> Callable:
    fn.__name__ = name
    fn.__qualname__ = f"run_gui.<patched>.{name}"
    fn._charart_patched = True  # type: ignore[attr-defined]
    return fn


def _wrap_refresh_art(orig):
    from charart_gui import refresh_art_logic as ral

    cm = _cell_map(orig)

    def refresh_art():
        ral(
            path=_deref(cm, "current_path").get()
            if hasattr(_deref(cm, "current_path"), "get")
            else _deref(cm, "current_path"),
            current_path_get=_deref(cm, "current_path").get
            if hasattr(_deref(cm, "current_path"), "get")
            else None,
            current_style_get=_deref(cm, "current_style").get,
            current_effect_get=_deref(cm, "current_effect").get,
            color_mode_get=lambda: bool(_deref(cm, "color_mode_var").get()),
            get_gui_width=_deref(cm, "get_gui_width"),
            get_gui_height=_deref(cm, "get_gui_height"),
            get_transparent_bg_rgb=_deref(cm, "get_transparent_bg_rgb"),
            stop_animation=_deref(cm, "stop_animation"),
            pad_to_display=_deref(cm, "pad_to_display"),
            show_code=_deref(cm, "show_code"),
            show_padded=_deref(cm, "show_padded"),
            show_progress_determinate=cm["show_progress_determinate"].cell_contents
            if "show_progress_determinate" in cm
            else None,
            show_progress_indeterminate=cm["show_progress_indeterminate"].cell_contents
            if "show_progress_indeterminate" in cm
            else None,
            close_progress=cm["close_progress"].cell_contents
            if "close_progress" in cm
            else None,
            update_progress=cm["update_progress"].cell_contents
            if "update_progress" in cm
            else None,
            play_next_frame=cm["play_next_frame"].cell_contents
            if "play_next_frame" in cm
            else None,
            update_foot_and_size=cm["update_foot_and_size"].cell_contents
            if "update_foot_and_size" in cm
            else None,
            update_preview_window=cm["update_preview_window"].cell_contents
            if "update_preview_window" in cm
            else None,
            messagebox_showerror=lambda title, key: _deref(cm, "messagebox").showerror(
                title, _deref(cm, "t")(key)
            ),
            anim_frames_data=_deref(cm, "anim_frames_data"),
            anim_frames_colors=_deref(cm, "anim_frames_colors"),
            anim_durations=_deref(cm, "anim_durations"),
            anim_index=_deref(cm, "anim_index"),
            root_update=_deref(cm, "root").update_idletasks,
            root_after=_deref(cm, "root").after,
            pad_color=_deref(cm, "_pad_color") if "_pad_color" in cm else (40, 22, 38),
        )

    return _patched(refresh_art, "refresh_art")


def _wrap_open_image(orig):
    from charart_gui import open_image_logic as oil

    c = _cells(orig)

    def open_image(path_from_dialog=None):
        oil(
            path_from_dialog=path_from_dialog,
            filedialog_askopenfilename=c["filedialog"].askopenfilename,
            current_path_set=c["current_path"].set,
            recent_paths=c["recent_paths"],
            save_last_path_fn=c["save_last_path"],
            save_recent_paths_fn=c["save_recent_paths"],
            refresh_recent_menu=c["refresh_recent_menu"],
            refresh_art_fn=c["refresh_art"],
            t=c["t"],
        )

    return _patched(open_image, "open_image")


def _wrap_stop_animation(orig):
    c = _cells(orig)

    def stop_animation():
        stop_animation_logic(
            c["anim_after_id"], c["anim_frames_data"],
            c["anim_frames_colors"], c["anim_durations"],
            c["root"].after_cancel,
        )

    return _patched(stop_animation, "stop_animation")


def _wrap_pad_to_display(orig):
    c = _cells(orig)

    def pad_to_display(lines, cw, ch, colors=None):
        return pad_to_display_fn(
            lines, cw, ch, colors,
            c["get_gui_width"], c["get_gui_height"], c["_pad_color"],
        )

    return _patched(pad_to_display, "pad_to_display")


def _wrap_get_art_text(orig):
    c = _cells(orig)

    def get_art_text():
        return get_art_text_logic(
            last_shown_code=c["last_shown_code"],
            anim_frames_data=c["anim_frames_data"],
            art_text_get=c["art_text"].get,
            tk_end=c["tk"].END,
        )

    return _patched(get_art_text, "get_art_text")


def _wrap_get_art_html(orig):
    c = _cells(orig)

    def get_art_html():
        return get_art_html_logic(
            last_shown_padded=c["last_shown_padded"],
            last_shown_colors=c["last_shown_colors"],
        )

    return _patched(get_art_html, "get_art_html")


def _wrap_copy_art(orig):
    c = _cells(orig)

    def copy_art():
        copy_art_logic(
            get_art_html=c["get_art_html"],
            get_art_text=c["get_art_text"],
            root_clipboard_clear=c["root"].clipboard_clear,
            root_clipboard_append=c["root"].clipboard_append,
            messagebox_showinfo=c["messagebox"].showinfo,
            messagebox_showwarning=c["messagebox"].showwarning,
            t=c["t"],
        )

    return _patched(copy_art, "copy_art")


def _wrap_export_txt(orig):
    c = _cells(orig)

    def export_txt():
        export_txt_logic(
            get_art_text=c["get_art_text"],
            filedialog_asksaveasfilename=c["filedialog"].asksaveasfilename,
            messagebox_showwarning=c["messagebox"].showwarning,
            messagebox_showinfo=c["messagebox"].showinfo,
            messagebox_showerror=c["messagebox"].showerror,
            t=c["t"],
        )

    return _patched(export_txt, "export_txt")


def _wrap_export_html(orig):
    c = _cells(orig)

    def export_html():
        export_html_logic(
            get_art_html=c["get_art_html"],
            filedialog_asksaveasfilename=c["filedialog"].asksaveasfilename,
            messagebox_showwarning=c["messagebox"].showwarning,
            messagebox_showinfo=c["messagebox"].showinfo,
            messagebox_showerror=c["messagebox"].showerror,
            t=c["t"],
        )

    return _patched(export_html, "export_html")


def _wrap_export_png(orig):
    c = _cells(orig)

    def export_png():
        export_png_logic(
            last_shown_padded=c["last_shown_padded"],
            last_shown_colors=c["last_shown_colors"],
            export_bg_var_get=c["export_bg_var"].get,
            filedialog_asksaveasfilename=c["filedialog"].asksaveasfilename,
            messagebox_showwarning=c["messagebox"].showwarning,
            messagebox_showinfo=c["messagebox"].showinfo,
            messagebox_showerror=c["messagebox"].showerror,
            t=c["t"],
            export_bg_options=c["EXPORT_BG_OPTIONS"],
        )

    return _patched(export_png, "export_png")


def _wrap_export_gif(orig):
    c = _cells(orig)

    def export_gif():
        export_gif_logic(
            anim_frames_data=c["anim_frames_data"],
            anim_frames_colors=c["anim_frames_colors"],
            anim_durations=c["anim_durations"],
            last_shown_padded=c["last_shown_padded"],
            last_shown_colors=c["last_shown_colors"],
            export_bg_var_get=c["export_bg_var"].get,
            filedialog_asksaveasfilename=c["filedialog"].asksaveasfilename,
            messagebox_showwarning=c["messagebox"].showwarning,
            messagebox_showinfo=c["messagebox"].showinfo,
            messagebox_showerror=c["messagebox"].showerror,
            t=c["t"],
            export_bg_options=c["EXPORT_BG_OPTIONS"],
        )

    return _patched(export_gif, "export_gif")


def _wrap_save_current_preset(orig):
    c = _cells(orig)

    def save_current_preset():
        save_current_preset_logic(
            simpledialog_askstring=c["simpledialog"].askstring,
            root=c["root"],
            get_gui_width=c["get_gui_width"],
            get_gui_height=c["get_gui_height"],
            current_style_get=c["current_style"].get,
            current_effect_get=c["current_effect"].get,
            color_mode_get=c["color_mode_var"].get,
            transparent_get=c["transparent_var"].get,
            zoom_get=c["zoom_var"].get,
            presets_dict=c["presets_dict"],
            save_presets_dict=c["save_presets_dict"],
            refresh_preset_menu=c["refresh_preset_menu"],
            refresh_ui_lang=c["refresh_ui_lang"],
            messagebox_showinfo=c["messagebox"].showinfo,
            t=c["t"],
        )

    return _patched(save_current_preset, "save_current_preset")


def _wrap_load_preset_by_name(orig):
    c = _cells(orig)

    def load_preset_by_name(name):
        load_preset_by_name_logic(
            name=name,
            presets_dict=c["presets_dict"],
            width_var_set=c["width_var"].set,
            height_var_set=c["height_var"].set,
            current_style_set=c["current_style"].set,
            current_effect_set=c["current_effect"].set,
            color_mode_set=c["color_mode_var"].set,
            transparent_set=c["transparent_var"].set,
            zoom_set=c["zoom_var"].set,
            on_size_or_zoom_change=c["on_size_or_zoom_change"],
        )

    return _patched(load_preset_by_name, "load_preset_by_name")


def _wrap_refresh_preset_menu(orig):
    c = _cells(orig)

    def refresh_preset_menu():
        refresh_preset_menu_logic(
            preset_menu=c["preset_menu"],
            tk_end=c["tk"].END,
            presets_dict=c["presets_dict"],
            t=c["t"],
            save_current_preset=c["save_current_preset"],
            load_preset_by_name=c["load_preset_by_name"],
            delete_preset=c["delete_preset"],
        )

    return _patched(refresh_preset_menu, "refresh_preset_menu")


def _wrap_show_drop_overlay(orig):
    c = _cells(orig)

    def show_drop_overlay():
        show_drop_overlay_logic(
            drop_overlay=c["drop_overlay"],
            drop_overlay_lbl=c["drop_overlay_lbl"],
            t=c["t"],
        )

    return _patched(show_drop_overlay, "show_drop_overlay")


def _wrap_hide_drop_overlay(orig):
    c = _cells(orig)

    def hide_drop_overlay():
        hide_drop_overlay_logic(drop_overlay=c["drop_overlay"])

    return _patched(hide_drop_overlay, "hide_drop_overlay")


def _wrap_on_drop_art(orig):
    c = _cells(orig)

    def on_drop_art(event):
        return on_drop_art_logic(
            event_data=event.data,
            hide_drop_overlay=c["hide_drop_overlay"],
            open_image=c["open_image"],
        )

    return _patched(on_drop_art, "on_drop_art")


def _wrap_on_drop_enter_art(orig):
    c = _cells(orig)

    def on_drop_enter_art(event):
        return on_drop_enter_art_logic(show_drop_overlay=c["show_drop_overlay"])

    return _patched(on_drop_enter_art, "on_drop_enter_art")


def _wrap_on_drop_leave_art(orig):
    c = _cells(orig)

    def on_drop_leave_art(event):
        on_drop_leave_art_logic(hide_drop_overlay=c["hide_drop_overlay"])

    return _patched(on_drop_leave_art, "on_drop_leave_art")


def _wrap_on_drop_windnd(orig):
    c = _cells(orig)

    def on_drop_windnd(files):
        on_drop_windnd_logic(files=files, open_image=c["open_image"])

    return _patched(on_drop_windnd, "on_drop_windnd")


def _wrap_on_drop_root(orig):
    c = _cells(orig)

    def on_drop_root(event):
        on_drop_root_logic(event_data=event.data, open_image=c["open_image"])

    return _patched(on_drop_root, "on_drop_root")


def _wrap_show_code(orig):
    cm = _cell_map(orig)

    def show_code(code_str, padded_keep=None):
        show_code_logic(
            code_str,
            padded_keep,
            last_shown_code=_deref(cm, "last_shown_code"),
            last_shown_padded=_deref(cm, "last_shown_padded"),
            last_shown_colors=_deref(cm, "last_shown_colors"),
            art_text=_deref(cm, "art_text"),
            tk=_deref(cm, "tk"),
            get_gui_width=_deref(cm, "get_gui_width"),
            get_gui_height=_deref(cm, "get_gui_height"),
            root=_deref(cm, "root"),
            update_scrollbar_visibility=_deref(cm, "update_scrollbar_visibility"),
        )

    return _patched(show_code, "show_code")


def _wrap_show_padded(orig):
    cm = _cell_map(orig)

    def show_padded(padded, padded_colors=None):
        show_padded_logic(
            padded,
            padded_colors,
            last_shown_code=_deref(cm, "last_shown_code"),
            last_shown_padded=_deref(cm, "last_shown_padded"),
            last_shown_colors=_deref(cm, "last_shown_colors"),
            art_text=_deref(cm, "art_text"),
            get_gui_width=_deref(cm, "get_gui_width"),
            get_gui_height=_deref(cm, "get_gui_height"),
            _pad_color=_deref(cm, "_pad_color"),
            tk=_deref(cm, "tk"),
            root=_deref(cm, "root"),
            update_scrollbar_visibility=_deref(cm, "update_scrollbar_visibility"),
        )

    return _patched(show_padded, "show_padded")


def _wrap_play_next_frame(orig):
    cm = _cell_map(orig)

    def play_next_frame():
        play_next_frame_logic(
            anim_frames_data=_deref(cm, "anim_frames_data"),
            anim_frames_colors=_deref(cm, "anim_frames_colors"),
            anim_index=_deref(cm, "anim_index"),
            anim_durations=_deref(cm, "anim_durations"),
            anim_speed=_deref(cm, "anim_speed"),
            anim_after_id=_deref(cm, "anim_after_id"),
            show_padded=_deref(cm, "show_padded"),
            play_next_frame=play_next_frame,
            root=_deref(cm, "root"),
        )

    return _patched(play_next_frame, "play_next_frame")


def _wrap_load_preview_photo(orig):
    cm = _cell_map(orig)

    def load_preview_photo(path, max_w=400):
        return load_preview_photo_logic(path, max_w, ImageTk=_deref(cm, "ImageTk"))

    return _patched(load_preview_photo, "load_preview_photo")


def _wrap_pil_to_photo(orig):
    cm = _cell_map(orig)

    def _pil_to_photo(img_pil, max_w=400):
        return pil_to_photo_logic(img_pil, max_w, ImageTk=_deref(cm, "ImageTk"))

    return _patched(_pil_to_photo, "_pil_to_photo")


def _wrap_stop_preview_gif(orig):
    cm = _cell_map(orig)

    def _stop_preview_gif():
        stop_preview_gif_logic(
            _deref(cm, "preview_after_id"),
            _deref(cm, "preview_photos"),
            _deref(cm, "preview_win"),
        )

    return _patched(_stop_preview_gif, "_stop_preview_gif")


def _wrap_preview_gif_next(orig):
    cm = _cell_map(orig)

    def _preview_gif_next(win, lbl, frame_idx, durations, max_w=400):
        preview_gif_next_logic(
            win,
            lbl,
            frame_idx,
            durations,
            max_w,
            preview_photos=_deref(cm, "preview_photos"),
            preview_after_id=_deref(cm, "preview_after_id"),
            preview_gif_next=_preview_gif_next,
        )

    return _patched(_preview_gif_next, "_preview_gif_next")


def _wrap_update_preview_window(orig):
    cm = _cell_map(orig)

    def update_preview_window():
        update_preview_window_logic(
            preview_win=_deref(cm, "preview_win"),
            preview_label=_deref(cm, "preview_label"),
            current_path_get=_deref(cm, "current_path").get,
            stop_preview_gif=_deref(cm, "_stop_preview_gif"),
            pil_to_photo=_deref(cm, "_pil_to_photo"),
            load_preview_photo=_deref(cm, "load_preview_photo"),
            preview_gif_next=_deref(cm, "_preview_gif_next"),
            preview_photos=_deref(cm, "preview_photos"),
            preview_photo=_deref(cm, "preview_photo"),
            t=_deref(cm, "t"),
        )

    return _patched(update_preview_window, "update_preview_window")


def _wrap_show_original(orig):
    cm = _cell_map(orig)

    def show_original():
        show_original_logic(
            current_path_get=_deref(cm, "current_path").get,
            messagebox_showinfo=lambda title, msg: _deref(cm, "messagebox").showinfo(title, msg),
            t=_deref(cm, "t"),
            preview_win=_deref(cm, "preview_win"),
            update_preview_window=_deref(cm, "update_preview_window"),
            stop_preview_gif=_deref(cm, "_stop_preview_gif"),
            pil_to_photo=_deref(cm, "_pil_to_photo"),
            load_preview_photo=_deref(cm, "load_preview_photo"),
            preview_photos=_deref(cm, "preview_photos"),
            preview_photo=_deref(cm, "preview_photo"),
            tk=_deref(cm, "tk"),
            root=_deref(cm, "root"),
            bg_deep=_deref(cm, "bg_deep"),
            bg_panel=_deref(cm, "bg_panel"),
            preview_gif_next=_deref(cm, "_preview_gif_next"),
            messagebox_showerror=lambda title, msg: _deref(cm, "messagebox").showerror(title, msg),
        )

    return _patched(show_original, "show_original")


def _wrap_batch_export(orig):
    from charart_gui_misc import batch_export_logic

    c = _cells(orig)

    def batch_export():
        batch_export_logic(
            filedialog=c["filedialog"],
            messagebox_showinfo=c["messagebox"].showinfo,
            t=c["t"],
            current_style_get=c["current_style"].get,
            current_effect_get=c["current_effect"].get,
            color_mode_get=c["color_mode_var"].get,
            get_transparent_bg_rgb=c["get_transparent_bg_rgb"],
            get_gui_width=c["get_gui_width"],
            get_gui_height=c["get_gui_height"],
            pad_to_display=c["pad_to_display"],
        )

    return _patched(batch_export, "batch_export")


def _wrap_on_closing(orig):
    from charart_gui_misc import on_closing_logic

    c = _cells(orig)

    def on_closing():
        on_closing_logic(
            save_recent_paths=c["save_recent_paths"],
            save_presets_dict=c["save_presets_dict"],
            save_last_path=c["save_last_path"],
            recent_paths=c["recent_paths"],
            presets_dict=c["presets_dict"],
            current_path_get=c["current_path"].get,
            root=c["root"],
        )

    return _patched(on_closing, "on_closing")


def _wrap_refresh_ui_lang(orig):
    from charart_gui_misc import refresh_ui_lang_logic

    c = _cells(orig)

    def refresh_ui_lang():
        refresh_ui_lang_logic(
            orig,
            root=c["root"],
            t=c["t"],
            lang_var_get=c["lang_var"].get,
            drop_overlay_lbl=c["drop_overlay_lbl"],
            refresh_preset_menu=c["refresh_preset_menu"],
            update_foot_and_size=c["update_foot_and_size"],
            preview_win=c["preview_win"],
            current_path_get=c["current_path"].get,
        )

    return _patched(refresh_ui_lang, "refresh_ui_lang")


def _wrap_delete_preset(orig):
    from charart_gui_misc import delete_preset_logic

    c = _cells(orig)

    def delete_preset():
        delete_preset_logic(
            presets_dict=c["presets_dict"],
            messagebox_showinfo=c["messagebox"].showinfo,
            root=c["root"],
            tk=c["tk"],
            bg_deep=c["bg_deep"],
            bg_panel=c["bg_panel"],
            accent_pink=c["accent_pink"],
            text_primary=c["text_primary"],
            t=c["t"],
            save_presets_dict=c["save_presets_dict"],
            refresh_preset_menu=c["refresh_preset_menu"],
            refresh_ui_lang=c["refresh_ui_lang"],
        )

    return _patched(delete_preset, "delete_preset")


def _wrap_refresh_recent_menu(orig):
    from charart_gui_misc import refresh_recent_menu_logic

    c = _cells(orig)

    def refresh_recent_menu():
        refresh_recent_menu_logic(
            recent_menu=c["recent_menu"],
            tk_end=c["tk"].END,
            recent_paths=c["recent_paths"],
            current_path_set=c["current_path"].set,
            refresh_art=c["refresh_art"],
        )

    return _patched(refresh_recent_menu, "refresh_recent_menu")


def _wrap_on_speed_change(orig):
    from charart_gui_misc import on_speed_change_logic

    c = _cells(orig)

    def on_speed_change(*_args):
        on_speed_change_logic(
            speed_choices=c["SPEED_CHOICES"],
            speed_var_get=c["speed_var"].get,
            anim_speed=c["anim_speed"],
        )

    return _patched(on_speed_change, "on_speed_change")


def _wrap_update_foot_and_size(orig):
    from charart_gui_misc import update_foot_and_size_logic

    c = _cells(orig)

    def update_foot_and_size():
        update_foot_and_size_logic(
            current_path_get=c["current_path"].get,
            get_gui_width=c["get_gui_width"],
            get_gui_height=c["get_gui_height"],
            anim_frames_data=c["anim_frames_data"],
            foot_label=c["foot_label"],
            t=c["t"],
        )

    return _patched(update_foot_and_size, "update_foot_and_size")


def _wrap_on_size_or_zoom_change(orig):
    from charart_gui_misc import on_size_or_zoom_change_logic

    c = _cells(orig)

    def on_size_or_zoom_change(*_args):
        on_size_or_zoom_change_logic(
            art_text=c["art_text"],
            get_gui_width=c["get_gui_width"],
            get_gui_height=c["get_gui_height"],
            mono_font=c["mono_font"],
            zoom_var_get=c["zoom_var"].get,
            current_path_get=c["current_path"].get,
            refresh_art=c["refresh_art"],
            update_foot_and_size=c["update_foot_and_size"],
            update_scrollbar_visibility=c["update_scrollbar_visibility"],
            root=c["root"],
        )

    return _patched(on_size_or_zoom_change, "on_size_or_zoom_change")


def _wrap_on_style_or_effect_change(orig):
    from charart_gui_misc import on_style_or_effect_change_logic

    c = _cells(orig)

    def on_style_or_effect_change(*_args):
        on_style_or_effect_change_logic(
            current_path_get=c["current_path"].get,
            refresh_art=c["refresh_art"],
        )

    return _patched(on_style_or_effect_change, "on_style_or_effect_change")


def _wrap_get_transparent_bg_rgb(orig):
    from charart_gui_misc import get_transparent_bg_rgb_logic

    c = _cells(orig)

    def get_transparent_bg_rgb():
        return get_transparent_bg_rgb_logic(
            transparent_var_get=c["transparent_var"].get,
            gen_transparent_bg=c.get("GEN_TRANSPARENT_BG"),
        )

    return _patched(get_transparent_bg_rgb, "get_transparent_bg_rgb")


def _wrap_get_gui_width(orig):
    from charart_gui_misc import get_gui_width_logic

    c = _cells(orig)

    def get_gui_width():
        return get_gui_width_logic(width_var_get=c["width_var"].get)

    return _patched(get_gui_width, "get_gui_width")


def _wrap_get_gui_height(orig):
    from charart_gui_misc import get_gui_height_logic

    c = _cells(orig)

    def get_gui_height():
        return get_gui_height_logic(height_var_get=c["height_var"].get)

    return _patched(get_gui_height, "get_gui_height")


def _wrap_update_scrollbar_visibility(orig):
    from charart_gui_misc import update_scrollbar_visibility_logic

    c = _cells(orig)

    def update_scrollbar_visibility():
        update_scrollbar_visibility_logic(
            art_text=c["art_text"],
            root=c["root"],
            tk=c["tk"],
            xscroll=c["xscroll"],
            yscroll=c["yscroll"],
        )

    return _patched(update_scrollbar_visibility, "update_scrollbar_visibility")


def _wrap_close_preview_if_open(orig):
    from charart_gui_misc import close_preview_if_open_logic

    c = _cells(orig)

    def close_preview_if_open(_e=None):
        close_preview_if_open_logic(preview_win=c["preview_win"])

    return _patched(close_preview_if_open, "close_preview_if_open")


# (local_name, detect_freevars_subset, wrapper_factory)
HOOK_SPECS: list[tuple[str, frozenset[str], Callable]] = [
    ("refresh_art", frozenset({"current_path", "stop_animation"}), _wrap_refresh_art),
    ("open_image", frozenset({"current_path", "refresh_art"}), _wrap_open_image),
    ("stop_animation", frozenset({"anim_after_id", "anim_frames_data"}), _wrap_stop_animation),
    ("pad_to_display", frozenset({"get_gui_width", "_pad_color"}), _wrap_pad_to_display),
    ("get_art_text", frozenset({"last_shown_code", "art_text"}), _wrap_get_art_text),
    ("get_art_html", frozenset({"last_shown_padded", "last_shown_colors"}), _wrap_get_art_html),
    ("copy_art", frozenset({"get_art_html", "get_art_text"}), _wrap_copy_art),
    ("export_txt", frozenset({"get_art_text", "filedialog"}), _wrap_export_txt),
    ("export_html", frozenset({"get_art_html", "filedialog"}), _wrap_export_html),
    ("export_png", frozenset({"last_shown_padded", "EXPORT_BG_OPTIONS"}), _wrap_export_png),
    ("export_gif", frozenset({"anim_frames_data", "EXPORT_BG_OPTIONS"}), _wrap_export_gif),
    ("save_current_preset", frozenset({"presets_dict", "simpledialog"}), _wrap_save_current_preset),
    ("load_preset_by_name", frozenset({"presets_dict", "width_var"}), _wrap_load_preset_by_name),
    ("refresh_preset_menu", frozenset({"preset_menu", "presets_dict"}), _wrap_refresh_preset_menu),
    ("show_drop_overlay", frozenset({"drop_overlay", "drop_overlay_lbl"}), _wrap_show_drop_overlay),
    ("hide_drop_overlay", frozenset({"drop_overlay"}), _wrap_hide_drop_overlay),
    ("on_drop_art", frozenset({"hide_drop_overlay", "open_image"}), _wrap_on_drop_art),
    ("on_drop_enter_art", frozenset({"show_drop_overlay"}), _wrap_on_drop_enter_art),
    ("on_drop_leave_art", frozenset({"hide_drop_overlay"}), _wrap_on_drop_leave_art),
    ("on_drop_windnd", frozenset({"open_image"}), _wrap_on_drop_windnd),
    ("on_drop_root", frozenset({"open_image"}), _wrap_on_drop_root),
    ("show_code", frozenset({"last_shown_code", "art_text", "update_scrollbar_visibility"}), _wrap_show_code),
    ("show_padded", frozenset({"last_shown_padded", "_pad_color", "art_text"}), _wrap_show_padded),
    ("play_next_frame", frozenset({"anim_frames_data", "anim_index", "show_padded"}), _wrap_play_next_frame),
    ("load_preview_photo", frozenset({"ImageTk"}), _wrap_load_preview_photo),
    ("_pil_to_photo", frozenset({"ImageTk"}), _wrap_pil_to_photo),
    ("_stop_preview_gif", frozenset({"preview_after_id", "preview_photos", "preview_win"}), _wrap_stop_preview_gif),
    ("_preview_gif_next", frozenset({"preview_photos", "preview_after_id"}), _wrap_preview_gif_next),
    ("update_preview_window", frozenset({"preview_win", "current_path", "_stop_preview_gif"}), _wrap_update_preview_window),
    ("show_original", frozenset({"preview_win", "current_path", "update_preview_window"}), _wrap_show_original),
    ("batch_export", frozenset({"filedialog", "pad_to_display"}), _wrap_batch_export),
    ("on_closing", frozenset({"recent_paths", "presets_dict", "root"}), _wrap_on_closing),
    ("refresh_ui_lang", frozenset({"root", "lang_var", "refresh_preset_menu"}), _wrap_refresh_ui_lang),
    ("delete_preset", frozenset({"presets_dict", "bg_deep", "refresh_preset_menu"}), _wrap_delete_preset),
    ("refresh_recent_menu", frozenset({"recent_menu", "recent_paths"}), _wrap_refresh_recent_menu),
    ("on_speed_change", frozenset({"speed_var", "anim_speed"}), _wrap_on_speed_change),
    ("update_foot_and_size", frozenset({"foot_label", "current_path", "anim_frames_data"}), _wrap_update_foot_and_size),
    ("on_size_or_zoom_change", frozenset({"art_text", "zoom_var", "refresh_art"}), _wrap_on_size_or_zoom_change),
    ("on_style_or_effect_change", frozenset({"current_path", "refresh_art"}), _wrap_on_style_or_effect_change),
    ("get_transparent_bg_rgb", frozenset({"transparent_var", "GEN_TRANSPARENT_BG"}), _wrap_get_transparent_bg_rgb),
    ("get_gui_width", frozenset({"width_var"}), _wrap_get_gui_width),
    ("get_gui_height", frozenset({"height_var"}), _wrap_get_gui_height),
    ("update_scrollbar_visibility", frozenset({"art_text", "xscroll", "yscroll"}), _wrap_update_scrollbar_visibility),
    ("close_preview_if_open", frozenset({"preview_win"}), _wrap_close_preview_if_open),
]


def _detect(orig, keys: frozenset[str]) -> bool:
    if not callable(orig) or not getattr(orig, "__closure__", None):
        return False
    fv = frozenset(orig.__code__.co_freevars)
    return keys.issubset(fv)


def patch_run_gui_closures(
    replace_closure_var,
    patch_widget_commands,
    debug_hook=None,
) -> bool:
    """在 run_gui 栈帧内批量替换闭包函数。"""
    patched_any = False
    for fi in inspect.stack():
        loc = fi.frame.f_locals
        if "refresh_art" not in loc and "export_txt" not in loc:
            continue
        root = loc.get("root")
        frame_patched = False

        for local_name, keys, factory in HOOK_SPECS:
            orig = loc.get(local_name)
            if not _detect(orig, keys) or getattr(orig, "_charart_patched", False):
                continue
            new_fn = factory(orig)
            replace_closure_var(fi.frame, local_name, new_fn)
            loc[local_name] = new_fn
            if root is not None and local_name not in (
                "get_art_text", "get_art_html", "pad_to_display",
                "hide_drop_overlay", "show_drop_overlay",
                "show_code", "show_padded", "play_next_frame",
                "load_preview_photo", "_pil_to_photo", "_stop_preview_gif",
                "_preview_gif_next", "update_preview_window",
            ):
                patch_widget_commands(root, orig, new_fn)
            frame_patched = True
            if debug_hook:
                debug_hook(f"patched {local_name}")

        if frame_patched:
            patched_any = True
            return True
        if getattr(loc.get("refresh_art"), "_charart_patched", False):
            return True
    return patched_any
