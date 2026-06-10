# -*- coding: utf-8 -*-
"""星薇字符画 — Tkinter GUI 主界面。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# --- DND：优先 tkinterdnd2，Windows 回退 windnd ---
HAS_DND = False
DND_KIND = ""
DND_FILES = None
TkinterDnD = None
windnd = None

try:
    from tkinterdnd2 import DND_FILES as _DND_FILES
    from tkinterdnd2 import TkinterDnD as _TkinterDnD

    DND_FILES = _DND_FILES
    TkinterDnD = _TkinterDnD
    HAS_DND = True
    DND_KIND = "tkinterdnd2"
except ImportError:
    if sys.platform == "win32":
        try:
            import windnd as _windnd

            windnd = _windnd
            HAS_DND = True
            DND_KIND = "windnd"
        except ImportError:
            pass

from charart_core import CHAR_STYLES, EFFECTS
from charart_display import pad_to_display as pad_to_display_fn
from charart_display import stop_animation_logic
from charart_dnd import (
    hide_drop_overlay_logic,
    on_drop_art_logic,
    on_drop_enter_art_logic,
    on_drop_leave_art_logic,
    on_drop_root_logic,
    on_drop_windnd_logic,
    show_drop_overlay_logic,
)
from charart_export import (
    copy_art_logic,
    export_gif_logic,
    export_html_logic,
    export_png_logic,
    export_txt_logic,
    get_art_html_logic,
    get_art_text_logic,
)
from charart_gui import (
    _config_dir,
    load_last_path,
    load_presets_dict,
    load_recent_paths,
    open_image_logic,
    refresh_art_logic,
    save_last_path,
    save_presets_dict,
    save_recent_paths,
)
from charart_gui_misc import (
    batch_export_logic,
    block_copy_logic,
    block_insert_logic,
    block_select_logic,
    close_preview_if_open_logic,
    close_progress_logic,
    delete_preset_logic,
    get_gui_height_logic,
    get_gui_width_logic,
    get_transparent_bg_rgb_logic,
    on_closing_logic,
    on_size_or_zoom_change_logic,
    on_size_preset_change_logic,
    on_speed_change_logic,
    on_style_or_effect_change_logic,
    open_author_bilibili_logic,
    rebuild_var_radiomenu,
    refresh_recent_menu_logic,
    refresh_ui_lang_logic,
    reset_size_default_logic,
    show_progress_determinate_logic,
    show_progress_indeterminate_logic,
    sync_size_and_refresh_logic,
    update_foot_and_size_logic,
    update_menubutton_var_label,
    update_progress_logic,
    update_scrollbar_visibility_logic,
)
from charart_i18n import (
    EXPORT_BG_OPTION_I18N,
    EXPORT_BG_OPTIONS,
    EXPORT_BG_VAR_OPTIONS,
    GEN_TRANSPARENT_BG,
    TRANSPARENT_OPTION_I18N,
    TRANSPARENT_VAR_OPTIONS,
    _t,
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
    show_original_logic,
    stop_preview_gif_logic,
    update_preview_window_logic,
)
from charart_show import play_next_frame_logic, show_code_logic, show_padded_logic

ROOT_DIR = Path(__file__).resolve().parent

BG_DEEP = "#1a0f1a"
BG_PANEL = "#281626"
ACCENT_PINK = "#ff9ec5"
TEXT_PRIMARY = "#fce4ec"

SIZE_PRESETS = [
    (40, 30), (50, 35), (68, 40), (80, 50),
    (100, 60), (120, 70), (160, 90), (200, 120),
]

SPEED_CHOICES = {"0.25x": 0.25, "0.5x": 0.5, "1x": 1.0, "2x": 2.0, "4x": 4.0}

_PAD_COLOR = (40, 22, 38)
_UI_FONT = ("Microsoft YaHei UI", 9)
_UI_FONT_SM = ("Microsoft YaHei UI", 8)
_UI_FONT_LG = ("Microsoft YaHei UI", 12, "bold")
_UI_FONT_BOLD = ("Microsoft YaHei UI", 9, "bold")


def _btn_kw(tk, bg=BG_PANEL, fg=ACCENT_PINK, **overrides):
    kw = dict(
        bg=bg,
        fg=fg,
        activebackground=ACCENT_PINK,
        activeforeground=BG_DEEP,
        relief=tk.FLAT,
        padx=10,
        pady=4,
        font=_UI_FONT,
        cursor="hand2",
    )
    kw.update(overrides)
    return kw


def run_gui_native() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
    from PIL import ImageTk

    base = str(ROOT_DIR)
    config_dir = str(_config_dir())
    default_path = os.path.join(base, "萝薇日常.png")
    if not os.path.isfile(default_path):
        default_path = ""

    recent_paths = load_recent_paths()
    presets_dict = load_presets_dict()
    initial_path = load_last_path() or default_path

    if HAS_DND and DND_KIND == "tkinterdnd2" and TkinterDnD is not None:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    root.title(_t("zh", "app_title"))
    root.resizable(True, True)
    root.configure(bg=BG_DEEP)

    # 窗口图标
    _icon_base = getattr(sys, "_MEIPASS", base)
    for png_name in ("图标.png", "icon.png"):
        _icon_png = os.path.join(_icon_base, png_name)
        if os.path.isfile(_icon_png):
            try:
                _icon_photo = tk.PhotoImage(file=_icon_png)
                root.iconphoto(True, _icon_photo)
                break
            except Exception:
                pass
    else:
        for ico_name in ("图标.ico", "icon.ico"):
            _icon_ico = os.path.join(_icon_base, ico_name)
            if os.path.isfile(_icon_ico):
                try:
                    root.iconbitmap(_icon_ico)
                    break
                except Exception:
                    pass

    width_var = tk.IntVar(value=68)
    height_var = tk.IntVar(value=40)
    size_preset_var = tk.StringVar(value="68×40")
    current_path = tk.StringVar(value=initial_path)
    current_style = tk.StringVar(value="默认")
    current_effect = tk.StringVar(value="正常")
    color_mode_var = tk.BooleanVar(value=True)
    transparent_var = tk.StringVar(value="透明")
    export_bg_var = tk.StringVar(value="透明")
    zoom_var = tk.IntVar(value=9)
    lang_var = tk.StringVar(value="zh")
    speed_var = tk.StringVar(value="1x")

    last_shown_padded: list = [None]
    last_shown_colors: list = [None]
    last_shown_code: list = [None]

    preview_win: list = [None]
    preview_label: list = [None]
    preview_photo: list = [None]
    preview_after_id: list = [None]
    preview_photos: list = []

    anim_after_id: list = [None]
    anim_frames_data: list = []
    anim_frames_colors: list = []
    anim_durations: list = []
    anim_index: list = [0]
    anim_speed: list = [1.0]

    progress_win_ref: list = [None]

    if sys.platform == "darwin":
        mono_font = ("Menlo", 9)
    else:
        mono_font = ("Consolas", 9)

    def t(key: str) -> str:
        return _t(lang_var.get(), key)

    def get_gui_width() -> int:
        return get_gui_width_logic(width_var_get=width_var.get)

    def get_gui_height() -> int:
        return get_gui_height_logic(height_var_get=height_var.get)

    def get_transparent_bg_rgb():
        return get_transparent_bg_rgb_logic(
            transparent_var_get=transparent_var.get,
            gen_transparent_bg=GEN_TRANSPARENT_BG,
        )

    # --- 闭包占位，稍后绑定 ---
    refresh_ui_lang = None  # type: ignore
    refresh_art = None  # type: ignore
    open_image = None  # type: ignore
    on_size_or_zoom_change = None  # type: ignore
    refresh_recent_menu = None  # type: ignore
    refresh_preset_menu = None  # type: ignore
    delete_preset = None  # type: ignore
    save_current_preset = None  # type: ignore
    load_preset_by_name = None  # type: ignore
    show_drop_overlay = None  # type: ignore
    hide_drop_overlay = None  # type: ignore
    update_scrollbar_visibility = None  # type: ignore
    update_foot_and_size = None  # type: ignore
    pad_to_display = None  # type: ignore
    stop_animation = None  # type: ignore
    show_code = None  # type: ignore
    show_padded = None  # type: ignore
    play_next_frame = None  # type: ignore
    update_preview_window = None  # type: ignore
    show_original = None  # type: ignore
    get_art_text = None  # type: ignore
    get_art_html = None  # type: ignore
    copy_art = None  # type: ignore
    export_txt = None  # type: ignore
    export_html = None  # type: ignore
    export_png = None  # type: ignore
    export_gif = None  # type: ignore
    batch_export = None  # type: ignore

    def _load_preview_photo(path, max_w=400):
        return load_preview_photo_logic(path, max_w, ImageTk=ImageTk)

    def _pil_to_photo(img_pil, max_w=400):
        return pil_to_photo_logic(img_pil, max_w, ImageTk=ImageTk)

    def _stop_preview_gif():
        stop_preview_gif_logic(preview_after_id, preview_photos, preview_win)

    def _preview_gif_next(win, lbl, frame_idx, durations, max_w=400):
        preview_gif_next_logic(
            win, lbl, frame_idx, durations, max_w,
            preview_photos=preview_photos,
            preview_after_id=preview_after_id,
            preview_gif_next=_preview_gif_next,
        )

    def show_progress_determinate(total: int):
        show_progress_determinate_logic(
            total,
            progress_win_ref=progress_win_ref,
            root=root,
            t=t,
            bg_deep=BG_DEEP,
            text_primary=TEXT_PRIMARY,
            tk=tk,
            ttk=ttk,
        )

    def update_progress(current: int, total: int):
        update_progress_logic(current, total, progress_win_ref=progress_win_ref, t=t)

    def show_progress_indeterminate():
        show_progress_indeterminate_logic(
            progress_win_ref=progress_win_ref,
            root=root,
            t=t,
            bg_deep=BG_DEEP,
            text_primary=TEXT_PRIMARY,
            tk=tk,
            ttk=ttk,
        )

    def close_progress():
        close_progress_logic(progress_win_ref=progress_win_ref)

    stop_animation = lambda: stop_animation_logic(
        anim_after_id, anim_frames_data, anim_frames_colors, anim_durations, root.after_cancel
    )

    pad_to_display = lambda lines, cw, ch, colors=None: pad_to_display_fn(
        lines, cw, ch, colors, get_gui_width, get_gui_height, _PAD_COLOR
    )

    # --- 工具栏 ---
    toolbar = tk.Frame(root, bg=BG_DEEP)
    toolbar.pack(fill=tk.X, padx=12, pady=(12, 6))

    toolbar_row1 = tk.Frame(toolbar, bg=BG_DEEP)
    toolbar_row1.pack(side=tk.TOP, fill=tk.X)

    toolbar_row2 = tk.Frame(toolbar, bg=BG_DEEP)
    toolbar_row2.pack(side=tk.TOP, fill=tk.X)

    def refresh_ui_lang_impl():
        refresh_ui_lang_logic(
            refresh_ui_lang,
            root=root,
            t=t,
            lang_var_get=lang_var.get,
            drop_overlay_lbl=drop_overlay_lbl,
            refresh_preset_menu=refresh_preset_menu,
            update_foot_and_size=update_foot_and_size,
            preview_win=preview_win,
            current_path_get=current_path.get,
        )

    refresh_ui_lang = refresh_ui_lang_impl

    def update_foot_and_size_impl():
        update_foot_and_size_logic(
            current_path_get=current_path.get,
            get_gui_width=get_gui_width,
            get_gui_height=get_gui_height,
            anim_frames_data=anim_frames_data,
            foot_label=foot_label,
            t=t,
        )

    update_foot_and_size = update_foot_and_size_impl

    def on_style_or_effect_change(*_args):
        on_style_or_effect_change_logic(
            current_path_get=current_path.get,
            refresh_art=refresh_art,
        )

    def on_size_or_zoom_change_impl(*_args):
        on_size_or_zoom_change_logic(
            art_text=art_text,
            get_gui_width=get_gui_width,
            get_gui_height=get_gui_height,
            mono_font=mono_font,
            zoom_var_get=zoom_var.get,
            current_path_get=current_path.get,
            refresh_art=refresh_art,
            update_foot_and_size=update_foot_and_size,
            update_scrollbar_visibility=update_scrollbar_visibility,
            root=root,
        )

    on_size_or_zoom_change = on_size_or_zoom_change_impl

    def refresh_art_impl():
        refresh_art_logic(
            path=current_path.get(),
            current_path_get=current_path.get,
            current_style_get=current_style.get,
            current_effect_get=current_effect.get,
            color_mode_get=lambda: bool(color_mode_var.get()),
            get_gui_width=get_gui_width,
            get_gui_height=get_gui_height,
            get_transparent_bg_rgb=get_transparent_bg_rgb,
            stop_animation=stop_animation,
            pad_to_display=pad_to_display,
            show_code=show_code,
            show_padded=show_padded,
            show_progress_determinate=show_progress_determinate,
            show_progress_indeterminate=show_progress_indeterminate,
            close_progress=close_progress,
            update_progress=update_progress,
            play_next_frame=play_next_frame,
            update_foot_and_size=update_foot_and_size,
            update_preview_window=update_preview_window,
            messagebox_showerror=lambda title, key: messagebox.showerror(title, t(key)),
            anim_frames_data=anim_frames_data,
            anim_frames_colors=anim_frames_colors,
            anim_durations=anim_durations,
            anim_index=anim_index,
            root_update=root.update_idletasks,
            root_after=root.after,
            pad_color=_PAD_COLOR,
        )

    refresh_art = refresh_art_impl

    def open_image_impl(path_from_dialog=None):
        open_image_logic(
            path_from_dialog=path_from_dialog,
            filedialog_askopenfilename=filedialog.askopenfilename,
            current_path_set=current_path.set,
            recent_paths=recent_paths,
            save_last_path_fn=lambda p: save_last_path(p),
            save_recent_paths_fn=lambda ps: save_recent_paths(ps),
            refresh_recent_menu=refresh_recent_menu,
            refresh_art_fn=refresh_art,
            t=t,
        )

    open_image = open_image_impl

    def update_preview_window_impl():
        update_preview_window_logic(
            preview_win=preview_win,
            preview_label=preview_label,
            current_path_get=current_path.get,
            stop_preview_gif=_stop_preview_gif,
            pil_to_photo=_pil_to_photo,
            load_preview_photo=_load_preview_photo,
            preview_gif_next=_preview_gif_next,
            preview_photos=preview_photos,
            preview_photo=preview_photo,
            t=t,
        )

    update_preview_window = update_preview_window_impl

    def show_original_impl():
        show_original_logic(
            current_path_get=current_path.get,
            messagebox_showinfo=lambda title, msg: messagebox.showinfo(title, msg),
            t=t,
            preview_win=preview_win,
            update_preview_window=update_preview_window,
            stop_preview_gif=_stop_preview_gif,
            pil_to_photo=_pil_to_photo,
            load_preview_photo=_load_preview_photo,
            preview_photos=preview_photos,
            preview_photo=preview_photo,
            tk=tk,
            root=root,
            bg_deep=BG_DEEP,
            bg_panel=BG_PANEL,
            preview_gif_next=_preview_gif_next,
            messagebox_showerror=lambda title, msg: messagebox.showerror(title, msg),
        )

    show_original = show_original_impl

    # refresh_art 依赖 show_code/show_padded/play_next_frame — 在 art_text 创建前定义逻辑
    def update_scrollbar_visibility_impl():
        update_scrollbar_visibility_logic(
            art_text=art_text,
            root=root,
            tk=tk,
            xscroll=xscroll,
            yscroll=yscroll,
        )

    update_scrollbar_visibility = update_scrollbar_visibility_impl

    def show_code_impl(code_str, padded_keep=None):
        show_code_logic(
            code_str,
            padded_keep,
            last_shown_code=last_shown_code,
            last_shown_padded=last_shown_padded,
            last_shown_colors=last_shown_colors,
            art_text=art_text,
            tk=tk,
            get_gui_width=get_gui_width,
            get_gui_height=get_gui_height,
            root=root,
            update_scrollbar_visibility=update_scrollbar_visibility,
        )

    show_code = show_code_impl

    def show_padded_impl(padded, padded_colors=None):
        show_padded_logic(
            padded,
            padded_colors,
            last_shown_code=last_shown_code,
            last_shown_padded=last_shown_padded,
            last_shown_colors=last_shown_colors,
            art_text=art_text,
            get_gui_width=get_gui_width,
            get_gui_height=get_gui_height,
            _pad_color=_PAD_COLOR,
            tk=tk,
            root=root,
            update_scrollbar_visibility=update_scrollbar_visibility,
        )

    show_padded = show_padded_impl

    def play_next_frame_impl():
        play_next_frame_logic(
            anim_frames_data=anim_frames_data,
            anim_frames_colors=anim_frames_colors,
            anim_index=anim_index,
            anim_durations=anim_durations,
            anim_speed=anim_speed,
            anim_after_id=anim_after_id,
            show_padded=show_padded,
            play_next_frame=play_next_frame_impl,
            root=root,
        )

    play_next_frame = play_next_frame_impl

    def get_art_text_impl():
        return get_art_text_logic(
            last_shown_code=last_shown_code,
            anim_frames_data=anim_frames_data,
            art_text_get=art_text.get,
            tk_end=tk.END,
        )

    get_art_text = get_art_text_impl

    def get_art_html_impl():
        return get_art_html_logic(
            last_shown_padded=last_shown_padded,
            last_shown_colors=last_shown_colors,
        )

    get_art_html = get_art_html_impl

    copy_art = lambda: copy_art_logic(
        get_art_html=get_art_html,
        get_art_text=get_art_text,
        root_clipboard_clear=root.clipboard_clear,
        root_clipboard_append=root.clipboard_append,
        messagebox_showinfo=messagebox.showinfo,
        messagebox_showwarning=messagebox.showwarning,
        t=t,
    )

    export_txt = lambda: export_txt_logic(
        get_art_text=get_art_text,
        filedialog_asksaveasfilename=filedialog.asksaveasfilename,
        messagebox_showwarning=messagebox.showwarning,
        messagebox_showinfo=messagebox.showinfo,
        messagebox_showerror=messagebox.showerror,
        t=t,
    )

    export_html = lambda: export_html_logic(
        get_art_html=get_art_html,
        filedialog_asksaveasfilename=filedialog.asksaveasfilename,
        messagebox_showwarning=messagebox.showwarning,
        messagebox_showinfo=messagebox.showinfo,
        messagebox_showerror=messagebox.showerror,
        t=t,
    )

    export_png = lambda: export_png_logic(
        last_shown_padded=last_shown_padded,
        last_shown_colors=last_shown_colors,
        export_bg_var_get=export_bg_var.get,
        filedialog_asksaveasfilename=filedialog.asksaveasfilename,
        messagebox_showwarning=messagebox.showwarning,
        messagebox_showinfo=messagebox.showinfo,
        messagebox_showerror=messagebox.showerror,
        t=t,
        export_bg_options=EXPORT_BG_OPTIONS,
    )

    export_gif = lambda: export_gif_logic(
        anim_frames_data=anim_frames_data,
        anim_frames_colors=anim_frames_colors,
        anim_durations=anim_durations,
        last_shown_padded=last_shown_padded,
        last_shown_colors=last_shown_colors,
        export_bg_var_get=export_bg_var.get,
        filedialog_asksaveasfilename=filedialog.asksaveasfilename,
        messagebox_showwarning=messagebox.showwarning,
        messagebox_showinfo=messagebox.showinfo,
        messagebox_showerror=messagebox.showerror,
        t=t,
        export_bg_options=EXPORT_BG_OPTIONS,
    )

    batch_export = lambda: batch_export_logic(
        filedialog=filedialog,
        messagebox_showinfo=messagebox.showinfo,
        t=t,
        current_style_get=current_style.get,
        current_effect_get=current_effect.get,
        color_mode_get=color_mode_var.get,
        get_transparent_bg_rgb=get_transparent_bg_rgb,
        get_gui_width=get_gui_width,
        get_gui_height=get_gui_height,
        pad_to_display=pad_to_display,
    )

    save_current_preset = lambda: save_current_preset_logic(
        simpledialog_askstring=simpledialog.askstring,
        root=root,
        get_gui_width=get_gui_width,
        get_gui_height=get_gui_height,
        current_style_get=current_style.get,
        current_effect_get=current_effect.get,
        color_mode_get=color_mode_var.get,
        transparent_get=transparent_var.get,
        zoom_get=zoom_var.get,
        presets_dict=presets_dict,
        save_presets_dict=lambda d: save_presets_dict(d),
        refresh_preset_menu=refresh_preset_menu,
        refresh_ui_lang=refresh_ui_lang,
        messagebox_showinfo=messagebox.showinfo,
        t=t,
    )

    def load_preset_by_name_impl(name):
        load_preset_by_name_logic(
            name=name,
            presets_dict=presets_dict,
            width_var_set=width_var.set,
            height_var_set=height_var.set,
            current_style_set=current_style.set,
            current_effect_set=current_effect.set,
            color_mode_set=color_mode_var.set,
            transparent_set=transparent_var.set,
            zoom_set=zoom_var.set,
            on_size_or_zoom_change=on_size_or_zoom_change,
        )

    load_preset_by_name = load_preset_by_name_impl

    def refresh_preset_menu_impl():
        refresh_preset_menu_logic(
            preset_menu=preset_menu,
            tk_end=tk.END,
            presets_dict=presets_dict,
            t=t,
            save_current_preset=save_current_preset,
            load_preset_by_name=load_preset_by_name,
            delete_preset=delete_preset,
        )

    refresh_preset_menu = refresh_preset_menu_impl

    delete_preset = lambda: delete_preset_logic(
        presets_dict=presets_dict,
        messagebox_showinfo=messagebox.showinfo,
        root=root,
        tk=tk,
        bg_deep=BG_DEEP,
        bg_panel=BG_PANEL,
        accent_pink=ACCENT_PINK,
        text_primary=TEXT_PRIMARY,
        t=t,
        save_presets_dict=lambda d: save_presets_dict(d),
        refresh_preset_menu=refresh_preset_menu,
        refresh_ui_lang=refresh_ui_lang,
    )

    def refresh_recent_menu_impl():
        refresh_recent_menu_logic(
            recent_menu=recent_menu,
            tk_end=tk.END,
            recent_paths=recent_paths,
            current_path_set=current_path.set,
            refresh_art=refresh_art,
        )

    refresh_recent_menu = refresh_recent_menu_impl

    # ========== 工具栏 row1 ==========
    lang_btn = tk.Menubutton(
        toolbar_row1,
        text=_t("zh", "lang_zh"),
        bg=BG_PANEL,
        fg=ACCENT_PINK,
        relief=tk.FLAT,
        font=_UI_FONT,
        cursor="hand2",
    )
    lang_menu = tk.Menu(lang_btn, tearoff=0)
    for code, key in (("zh", "lang_zh"), ("zh_TW", "lang_zh_TW"), ("en", "lang_en"), ("ja", "lang_ja")):
        lang_menu.add_radiobutton(
            label=_t(code, key),
            variable=lang_var,
            value=code,
            command=refresh_ui_lang,
        )
    lang_btn["menu"] = lang_menu
    lang_btn.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.lang_btn = lang_btn

    btn_open = tk.Button(toolbar_row1, text=t("btn_open"), command=lambda: open_image(), **_btn_kw(tk))
    btn_open.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_open = btn_open

    on_size_preset_change = lambda val: on_size_preset_change_logic(
        val,
        size_presets=SIZE_PRESETS,
        width_var_set=width_var.set,
        height_var_set=height_var.set,
        on_size_or_zoom_change=on_size_or_zoom_change,
    )

    size_preset_labels = ["%d×%d" % (w, h) for w, h in SIZE_PRESETS]
    lbl_size_preset = tk.Label(
        toolbar_row1, text=t("lbl_size_preset"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT
    )
    lbl_size_preset.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_size_preset = lbl_size_preset

    size_preset_menu = tk.OptionMenu(toolbar_row1, size_preset_var, *size_preset_labels, command=on_size_preset_change)
    size_preset_menu.configure(bg=BG_PANEL, fg=TEXT_PRIMARY, relief=tk.FLAT, font=_UI_FONT)
    size_preset_menu.pack(side=tk.LEFT, padx=(0, 4))

    lbl_width = tk.Label(toolbar_row1, text=t("lbl_width"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT)
    lbl_width.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_width = lbl_width

    width_spin = tk.Spinbox(
        toolbar_row1, from_=8, to=200, width=4, textvariable=width_var,
        bg=BG_PANEL, fg=TEXT_PRIMARY, font=_UI_FONT,
    )
    width_spin.pack(side=tk.LEFT, padx=(0, 2))

    sync_size_and_refresh = lambda *_a: sync_size_and_refresh_logic(
        width_var_get=width_var.get,
        height_var_get=height_var.get,
        size_presets=SIZE_PRESETS,
        size_preset_var_set=size_preset_var.set,
        on_size_or_zoom_change=on_size_or_zoom_change,
        root=root,
    )
    width_var.trace_add("write", sync_size_and_refresh)

    lbl_height = tk.Label(toolbar_row1, text=t("lbl_height"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT)
    lbl_height.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_height = lbl_height

    height_spin = tk.Spinbox(
        toolbar_row1, from_=6, to=120, width=4, textvariable=height_var,
        bg=BG_PANEL, fg=TEXT_PRIMARY, font=_UI_FONT,
    )
    height_spin.pack(side=tk.LEFT, padx=(0, 4))
    height_var.trace_add("write", sync_size_and_refresh)

    reset_size_default = lambda: reset_size_default_logic(
        width_var_set=width_var.set,
        height_var_set=height_var.set,
        size_preset_var_set=size_preset_var.set,
        on_size_or_zoom_change=on_size_or_zoom_change,
    )

    btn_reset = tk.Button(
        toolbar_row1,
        text=t("btn_reset"),
        command=reset_size_default,
        **_btn_kw(tk, padx=6, pady=2, font=_UI_FONT_SM),
    )
    btn_reset.pack(side=tk.LEFT, padx=(0, 6))
    refresh_ui_lang.btn_reset = btn_reset

    lbl_transparent = tk.Label(
        toolbar_row1, text=t("lbl_transparent"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT
    )
    lbl_transparent.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_transparent = lbl_transparent

    trans_btn = tk.Menubutton(
        toolbar_row1,
        bg=BG_PANEL,
        fg=TEXT_PRIMARY,
        relief=tk.FLAT,
        font=_UI_FONT,
        cursor="hand2",
    )
    trans_menu = tk.Menu(trans_btn, tearoff=0)
    trans_btn["menu"] = trans_menu
    rebuild_var_radiomenu(
        trans_menu, tk.END, transparent_var,
        TRANSPARENT_VAR_OPTIONS, TRANSPARENT_OPTION_I18N, t,
        on_change=on_style_or_effect_change,
    )
    update_menubutton_var_label(trans_btn, transparent_var, TRANSPARENT_OPTION_I18N, t)
    trans_btn.pack(side=tk.LEFT, padx=(0, 6))
    refresh_ui_lang.trans_btn = trans_btn
    refresh_ui_lang.trans_menu = trans_menu
    refresh_ui_lang.transparent_var = transparent_var
    refresh_ui_lang.transparent_options = TRANSPARENT_VAR_OPTIONS
    refresh_ui_lang.transparent_i18n = TRANSPARENT_OPTION_I18N
    refresh_ui_lang.tk_end = tk.END

    lbl_style = tk.Label(toolbar_row1, text=t("lbl_style"), fg=ACCENT_PINK, bg=BG_DEEP, font=_UI_FONT)
    lbl_style.pack(side=tk.LEFT, padx=(0, 4))
    refresh_ui_lang.lbl_style = lbl_style

    style_btn = tk.Menubutton(
        toolbar_row1,
        textvariable=current_style,
        bg=BG_PANEL,
        fg=ACCENT_PINK,
        activebackground=ACCENT_PINK,
        activeforeground=BG_DEEP,
        relief=tk.FLAT,
        highlightbackground="#806070",
        highlightthickness=1,
        padx=8,
        pady=4,
        font=_UI_FONT_BOLD,
        direction="below",
        cursor="hand2",
    )
    style_menu = tk.Menu(style_btn, tearoff=0)
    for name in CHAR_STYLES:
        style_menu.add_radiobutton(
            label=name, variable=current_style, value=name, command=on_style_or_effect_change
        )
    style_btn["menu"] = style_menu
    style_btn.pack(side=tk.LEFT, padx=(0, 6))

    lbl_effect = tk.Label(toolbar_row1, text=t("lbl_effect"), fg=ACCENT_PINK, bg=BG_DEEP, font=_UI_FONT)
    lbl_effect.pack(side=tk.LEFT, padx=(0, 4))
    refresh_ui_lang.lbl_effect = lbl_effect

    effect_btn = tk.Menubutton(
        toolbar_row1,
        textvariable=current_effect,
        bg=BG_PANEL,
        fg=ACCENT_PINK,
        activebackground=ACCENT_PINK,
        activeforeground=BG_DEEP,
        relief=tk.FLAT,
        highlightbackground="#806070",
        highlightthickness=1,
        padx=8,
        pady=4,
        font=_UI_FONT_BOLD,
        direction="below",
        cursor="hand2",
    )
    effect_menu = tk.Menu(effect_btn, tearoff=0)
    for name in EFFECTS:
        effect_menu.add_radiobutton(
            label=name, variable=current_effect, value=name, command=on_style_or_effect_change
        )
    effect_btn["menu"] = effect_menu
    effect_btn.pack(side=tk.LEFT, padx=(0, 8))

    cb_color = tk.Checkbutton(
        toolbar_row1,
        text=t("lbl_color_mode"),
        variable=color_mode_var,
        command=on_style_or_effect_change,
        bg=BG_DEEP,
        fg=ACCENT_PINK,
        activebackground=BG_DEEP,
        activeforeground=ACCENT_PINK,
        selectcolor=BG_PANEL,
        font=_UI_FONT,
        cursor="hand2",
    )
    cb_color.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.cb_color = cb_color

    btn_copy = tk.Button(toolbar_row1, text=t("btn_copy"), command=copy_art, **_btn_kw(tk))
    btn_copy.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_copy = btn_copy

    # ========== 工具栏 row2 ==========
    btn_original = tk.Button(toolbar_row2, text=t("btn_original"), command=show_original, **_btn_kw(tk))
    btn_original.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_original = btn_original

    lbl_export_bg = tk.Label(
        toolbar_row2, text=t("lbl_export_bg"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT
    )
    lbl_export_bg.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_export_bg = lbl_export_bg

    export_bg_btn = tk.Menubutton(
        toolbar_row2,
        bg=BG_PANEL,
        fg=TEXT_PRIMARY,
        relief=tk.FLAT,
        font=_UI_FONT,
        cursor="hand2",
    )
    export_bg_menu = tk.Menu(export_bg_btn, tearoff=0)
    export_bg_btn["menu"] = export_bg_menu
    rebuild_var_radiomenu(
        export_bg_menu, tk.END, export_bg_var,
        EXPORT_BG_VAR_OPTIONS, EXPORT_BG_OPTION_I18N, t,
    )
    update_menubutton_var_label(export_bg_btn, export_bg_var, EXPORT_BG_OPTION_I18N, t)
    export_bg_btn.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.export_bg_btn = export_bg_btn
    refresh_ui_lang.export_bg_menu = export_bg_menu
    refresh_ui_lang.export_bg_var = export_bg_var
    refresh_ui_lang.export_bg_options = EXPORT_BG_VAR_OPTIONS
    refresh_ui_lang.export_bg_i18n = EXPORT_BG_OPTION_I18N

    btn_export_txt = tk.Button(toolbar_row2, text=t("btn_export_txt"), command=export_txt, **_btn_kw(tk))
    btn_export_txt.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_export_txt = btn_export_txt

    btn_export_html = tk.Button(toolbar_row2, text=t("btn_export_html"), command=export_html, **_btn_kw(tk))
    btn_export_html.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_export_html = btn_export_html

    btn_export_png = tk.Button(toolbar_row2, text=t("btn_export_png"), command=export_png, **_btn_kw(tk))
    btn_export_png.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_export_png = btn_export_png

    btn_export_gif = tk.Button(toolbar_row2, text=t("btn_export_gif"), command=export_gif, **_btn_kw(tk))
    btn_export_gif.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_export_gif = btn_export_gif

    btn_batch = tk.Button(toolbar_row2, text=t("btn_batch"), command=batch_export, **_btn_kw(tk))
    btn_batch.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_batch = btn_batch

    recent_btn = tk.Menubutton(
        toolbar_row2, text=t("lbl_recent"), bg=BG_PANEL, fg=ACCENT_PINK,
        relief=tk.FLAT, font=_UI_FONT, cursor="hand2",
    )
    recent_menu = tk.Menu(recent_btn, tearoff=0)
    recent_btn["menu"] = recent_menu
    refresh_recent_menu()
    recent_btn.pack(side=tk.LEFT, padx=(0, 4))
    refresh_ui_lang.recent_btn = recent_btn

    preset_btn = tk.Menubutton(
        toolbar_row2, text=t("lbl_preset"), bg=BG_PANEL, fg=ACCENT_PINK,
        relief=tk.FLAT, font=_UI_FONT, cursor="hand2",
    )
    preset_menu = tk.Menu(preset_btn, tearoff=0)
    refresh_preset_menu()
    preset_btn["menu"] = preset_menu
    preset_btn.pack(side=tk.LEFT, padx=(0, 4))
    refresh_ui_lang.preset_btn = preset_btn

    btn_follow_author = tk.Button(
        toolbar_row2, text=t("btn_follow_author"), command=open_author_bilibili_logic, **_btn_kw(tk)
    )
    btn_follow_author.pack(side=tk.LEFT, padx=(0, 8))
    refresh_ui_lang.btn_follow_author = btn_follow_author

    on_speed_change = lambda *_: on_speed_change_logic(
        speed_choices=SPEED_CHOICES,
        speed_var_get=speed_var.get,
        anim_speed=anim_speed,
    )

    lbl_speed = tk.Label(toolbar_row2, text=t("lbl_speed"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT)
    lbl_speed.pack(side=tk.LEFT, padx=(0, 4))
    refresh_ui_lang.lbl_speed = lbl_speed

    speed_menu = tk.OptionMenu(
        toolbar_row2, speed_var, *SPEED_CHOICES.keys(), command=on_speed_change
    )
    speed_menu.configure(bg=BG_PANEL, fg=TEXT_PRIMARY, relief=tk.FLAT, font=_UI_FONT)
    speed_menu.pack(side=tk.LEFT, padx=(0, 8))

    lbl_zoom = tk.Label(toolbar_row2, text=t("lbl_zoom"), fg=TEXT_PRIMARY, bg=BG_DEEP, font=_UI_FONT)
    lbl_zoom.pack(side=tk.LEFT, padx=(0, 2))
    refresh_ui_lang.lbl_zoom = lbl_zoom

    zoom_menu = tk.OptionMenu(
        toolbar_row2, zoom_var, *list(range(8, 17)),
        command=lambda *_: on_size_or_zoom_change(),
    )
    zoom_menu.configure(bg=BG_PANEL, fg=TEXT_PRIMARY, relief=tk.FLAT, font=_UI_FONT)
    zoom_var.trace_add(
        "write",
        lambda *_: root.after(50, on_size_or_zoom_change),
    )
    zoom_menu.pack(side=tk.LEFT, padx=(0, 4))

    # ========== 主画布 ==========
    title_label = tk.Label(
        root, text=t("title_art"), fg=ACCENT_PINK, bg=BG_DEEP, font=_UI_FONT_LG
    )
    title_label.pack(pady=(0, 6))
    refresh_ui_lang.title_label = title_label

    art_frame = tk.Frame(root, bg=BG_PANEL, padx=16, pady=12)
    art_frame.pack(padx=12, pady=(0, 8), fill=tk.BOTH, expand=True)
    art_frame.configure(takefocus=1)

    art_inner = tk.Frame(art_frame, bg=BG_PANEL)
    art_inner.pack(expand=True, fill=tk.NONE)

    yscroll = tk.Scrollbar(
        art_inner, bg=BG_PANEL, troughcolor=BG_DEEP, activebackground=ACCENT_PINK
    )
    xscroll = tk.Scrollbar(
        art_frame, orient=tk.HORIZONTAL, bg=BG_PANEL, troughcolor=BG_DEEP, activebackground=ACCENT_PINK
    )

    art_text = tk.Text(
        art_inner,
        width=get_gui_width() + 1,
        height=get_gui_height() + 1,
        font=mono_font,
        fg=TEXT_PRIMARY,
        bg=BG_PANEL,
        insertbackground=ACCENT_PINK,
        relief=tk.FLAT,
        borderwidth=0,
        padx=4,
        pady=4,
        cursor="arrow",
        takefocus=0,
        insertwidth=0,
        wrap=tk.NONE,
        yscrollcommand=yscroll.set,
        xscrollcommand=xscroll.set,
    )
    art_text.pack(side=tk.LEFT, fill=tk.NONE)
    yscroll.config(command=art_text.yview)
    xscroll.config(command=art_text.xview)

    drop_overlay = tk.Frame(art_frame, bg=BG_PANEL, highlightbackground=ACCENT_PINK, highlightthickness=2)
    drop_overlay_lbl = tk.Label(
        drop_overlay, text="", fg=ACCENT_PINK, bg=BG_PANEL, font=("Microsoft YaHei UI", 14, "bold")
    )
    drop_overlay_lbl.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    show_drop_overlay = lambda: show_drop_overlay_logic(
        drop_overlay=drop_overlay, drop_overlay_lbl=drop_overlay_lbl, t=t
    )
    hide_drop_overlay = lambda: hide_drop_overlay_logic(drop_overlay=drop_overlay)

    art_text.bind("<Key>", block_insert_logic)
    art_text.bind("<Control-c>", block_copy_logic)
    art_text.bind("<Control-a>", block_copy_logic)
    art_text.bind("<Button-1>", block_select_logic)
    art_text.bind("<B1-Motion>", block_select_logic)
    art_text.bind("<Double-Button-1>", block_select_logic)
    art_text.bind("<Triple-Button-1>", block_select_logic)
    art_text.bind("<Shift-Button-1>", block_select_logic)
    art_text.bind("<ButtonRelease-1>", block_select_logic)
    art_text.bind("<FocusIn>", lambda _e: art_frame.focus_set())
    art_text.configure(state=tk.DISABLED)

    foot_label = tk.Label(
        root,
        text=t("foot_open") % (get_gui_width(), get_gui_height()),
        fg="#a08090",
        bg=BG_DEEP,
        font=_UI_FONT,
    )
    foot_label.pack(pady=(0, 4))
    update_foot_and_size()

    disclaimer_label = tk.Label(
        root,
        text=t("disclaimer"),
        fg="#706070",
        bg=BG_DEEP,
        font=_UI_FONT_SM,
        wraplength=680,
        justify=tk.CENTER,
    )
    disclaimer_label.pack(pady=(0, 12))
    refresh_ui_lang.disclaimer_label = disclaimer_label

    if initial_path and os.path.isfile(initial_path):
        refresh_art()

    # 快捷键
    root.bind("<Control-o>", lambda _e: open_image())
    root.bind("<Control-O>", lambda _e: open_image())
    root.bind("<Control-c>", lambda _e: copy_art())
    root.bind("<Control-s>", lambda _e: export_txt())
    root.bind("<Control-h>", lambda _e: export_html())

    close_preview_if_open = lambda _e=None: close_preview_if_open_logic(preview_win=preview_win)
    root.bind("<Escape>", close_preview_if_open)

    # 拖拽
    if HAS_DND and DND_KIND == "tkinterdnd2" and DND_FILES is not None:
        on_drop_root = lambda event: on_drop_root_logic(
            event_data=event.data, open_image=open_image
        )
        on_drop_art = lambda event: on_drop_art_logic(
            event_data=event.data,
            hide_drop_overlay=hide_drop_overlay,
            open_image=open_image,
        )
        on_drop_enter_art = lambda event: on_drop_enter_art_logic(show_drop_overlay=show_drop_overlay)
        on_drop_leave_art = lambda event: on_drop_leave_art_logic(hide_drop_overlay=hide_drop_overlay)

        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", on_drop_root)
        art_frame.drop_target_register(DND_FILES)
        art_frame.dnd_bind("<<DropEnter>>", on_drop_enter_art)
        art_frame.dnd_bind("<<DropLeave>>", on_drop_leave_art)
        art_frame.dnd_bind("<<Drop>>", on_drop_art)

    elif HAS_DND and DND_KIND == "windnd" and windnd is not None:
        def on_drop_windnd_overlay(files):
            show_drop_overlay()
            try:
                on_drop_windnd_logic(files=files, open_image=open_image)
            finally:
                hide_drop_overlay()

        windnd.hook_dropfiles(root, func=on_drop_windnd_overlay)
        try:
            windnd.hook_dropfiles(art_frame, func=on_drop_windnd_overlay)
        except Exception:
            pass

    root.update_idletasks()

    if sys.platform == "win32":
        root.minsize(640, 400)
        root.maxsize(root.winfo_screenwidth(), root.winfo_screenheight())
        try:
            root.state("zoomed")
        except Exception:
            pass
    else:
        try:
            root.attributes("-zoomed", True)
        except Exception:
            pass

    def on_closing():
        on_closing_logic(
            save_recent_paths=lambda ps: save_recent_paths(ps),
            save_presets_dict=lambda d: save_presets_dict(d),
            save_last_path=lambda p: save_last_path(p),
            recent_paths=recent_paths,
            presets_dict=presets_dict,
            current_path_get=current_path.get,
            root=root,
        )

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    run_gui_native()
