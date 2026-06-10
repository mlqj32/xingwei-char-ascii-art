# -*- coding: utf-8 -*-
"""GUI 辅助：进度条、滚动条、批量导出、界面语言等。"""
from __future__ import annotations

import os
import webbrowser
from typing import Any, Callable

from charart_core import CHAR_STYLES, EFFECTS, _charart_from_pil, get_animated_frames
from charart_i18n import GEN_TRANSPARENT_BG


def get_gui_width_logic(*, width_var_get: Callable[[], Any]) -> int:
    try:
        return max(8, min(200, int(width_var_get())))
    except (TypeError, ValueError):
        return 68


def get_gui_height_logic(*, height_var_get: Callable[[], Any]) -> int:
    try:
        return max(6, min(120, int(height_var_get())))
    except (TypeError, ValueError):
        return 40


def get_transparent_bg_rgb_logic(
    *,
    transparent_var_get: Callable[[], str],
    gen_transparent_bg: dict | None = None,
) -> tuple[int, int, int] | None:
    opts = gen_transparent_bg or GEN_TRANSPARENT_BG
    return opts.get(transparent_var_get(), (0, 0, 0))


def show_progress_determinate_logic(
    total: int,
    *,
    progress_win_ref: list,
    root,
    t: Callable[[str], str],
    bg_deep: str,
    text_primary: str,
    tk,
    ttk,
) -> None:
    if progress_win_ref[0]:
        try:
            progress_win_ref[0][0].destroy()
        except Exception:
            pass

    win = tk.Toplevel(root)
    win.title(t("progress_loading"))
    win.configure(bg=bg_deep)
    win.resizable(False, False)
    win.transient(root)

    lbl = tk.Label(
        win,
        text=t("progress_frame") % (0, total),
        fg=text_primary,
        bg=bg_deep,
        font=("Microsoft YaHei UI", 9),
    )
    lbl.pack(pady=(12, 6), padx=16)

    bar = ttk.Progressbar(
        win, length=280, maximum=100, value=0, mode="determinate"
    )
    bar.pack(pady=(0, 12), padx=16)
    win.update_idletasks()
    progress_win_ref[0] = (win, bar, lbl)


def update_progress_logic(
    current: int,
    total: int,
    *,
    progress_win_ref: list,
    t: Callable[[str], str],
) -> None:
    if not progress_win_ref[0] or total <= 0:
        return
    try:
        win, bar, lbl = progress_win_ref[0]
        if not win.winfo_exists():
            return
        bar["value"] = min(100.0, 100.0 * current / total)
        lbl["text"] = t("progress_frame") % (current, total)
    except Exception:
        pass


def show_progress_indeterminate_logic(
    *,
    progress_win_ref: list,
    root,
    t: Callable[[str], str],
    bg_deep: str,
    text_primary: str,
    tk,
    ttk,
) -> None:
    if progress_win_ref[0]:
        try:
            progress_win_ref[0][0].destroy()
        except Exception:
            pass

    win = tk.Toplevel(root)
    win.title(t("progress_loading"))
    win.configure(bg=bg_deep)
    win.resizable(False, False)
    win.transient(root)

    lbl = tk.Label(
        win,
        text=t("foot_loading"),
        fg=text_primary,
        bg=bg_deep,
        font=("Microsoft YaHei UI", 9),
    )
    lbl.pack(pady=(12, 6), padx=16)

    bar = ttk.Progressbar(win, length=280, mode="indeterminate")
    bar.pack(pady=(0, 12), padx=16)
    bar.start(8)
    win.update_idletasks()
    progress_win_ref[0] = (win, bar, lbl)


def close_progress_logic(*, progress_win_ref: list) -> None:
    if not progress_win_ref[0]:
        return
    try:
        win, bar, _lbl = progress_win_ref[0]
        if bar.cget("mode") == "indeterminate":
            bar.stop()
        win.destroy()
    except Exception:
        pass
    progress_win_ref[0] = None


def update_foot_and_size_logic(
    *,
    current_path_get: Callable[[], str],
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    anim_frames_data: list,
    foot_label,
    t: Callable[[str], str],
) -> None:
    path = current_path_get()
    gw = get_gui_width()
    gh = get_gui_height()

    if path and os.path.isfile(path):
        base_name = os.path.basename(path)
        if anim_frames_data:
            foot_label.configure(
                text=t("foot_anim") % (base_name, len(anim_frames_data), gw, gh)
            )
        else:
            foot_label.configure(text=t("foot_file") % (base_name, gw, gh))
    else:
        foot_label.configure(text=t("foot_open") % (gw, gh))


def on_size_or_zoom_change_logic(
    *,
    art_text,
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    mono_font: tuple,
    zoom_var_get: Callable[[], Any],
    current_path_get: Callable[[], str],
    refresh_art: Callable[[], None],
    update_foot_and_size: Callable[[], None],
    update_scrollbar_visibility: Callable[[], None],
    root,
) -> None:
    gw = get_gui_width()
    gh = get_gui_height()
    art_text.configure(width=gw + 1, height=gh + 1)
    art_text.configure(font=(mono_font[0], zoom_var_get()))
    update_foot_and_size()
    path = current_path_get()
    if path and os.path.isfile(path):
        refresh_art()
    else:
        update_foot_and_size()
    root.after(100, update_scrollbar_visibility)


def on_style_or_effect_change_logic(
    *,
    current_path_get: Callable[[], str],
    refresh_art: Callable[[], None],
) -> None:
    path = current_path_get()
    if path and os.path.isfile(path):
        refresh_art()


def on_size_preset_change_logic(
    val: str,
    *,
    size_presets: list[tuple[int, int]],
    width_var_set: Callable[[int], None],
    height_var_set: Callable[[int], None],
    on_size_or_zoom_change: Callable[[], None],
) -> None:
    for w, h in size_presets:
        if val == "%d×%d" % (w, h):
            width_var_set(w)
            height_var_set(h)
            on_size_or_zoom_change()
            return


def sync_size_and_refresh_logic(
    *_args: Any,
    width_var_get: Callable[[], Any],
    height_var_get: Callable[[], Any],
    size_presets: list[tuple[int, int]],
    size_preset_var_set: Callable[[str], None],
    on_size_or_zoom_change: Callable[[], None],
    root,
) -> None:
    try:
        w = int(width_var_get())
        h = int(height_var_get())
        for pw, ph in size_presets:
            if w == pw and h == ph:
                size_preset_var_set("%d×%d" % (pw, ph))
                break
    except (TypeError, ValueError):
        pass
    root.after(100, on_size_or_zoom_change)


def reset_size_default_logic(
    *,
    width_var_set: Callable[[int], None],
    height_var_set: Callable[[int], None],
    size_preset_var_set: Callable[[str], None],
    on_size_or_zoom_change: Callable[[], None],
) -> None:
    width_var_set(68)
    height_var_set(40)
    size_preset_var_set("68×40")
    on_size_or_zoom_change()


def on_speed_change_logic(
    *_args: Any,
    speed_choices: dict[str, float],
    speed_var_get: Callable[[], str],
    anim_speed: list,
) -> None:
    anim_speed[0] = speed_choices.get(speed_var_get(), 1.0)


def refresh_recent_menu_logic(
    *,
    recent_menu,
    tk_end,
    recent_paths: list[str],
    current_path_set: Callable[[str], None],
    refresh_art: Callable[[], None],
) -> None:
    recent_menu.delete(0, tk_end)
    for p in recent_paths:
        if len(p) < 50:
            short = os.path.basename(p)
        else:
            short = os.path.basename(p)[:47] + "..."
        recent_menu.add_command(
            label=short,
            command=lambda pth=p: (
                current_path_set(pth),
                refresh_art(),
            ),
        )


def delete_preset_logic(
    *,
    presets_dict: dict,
    messagebox_showinfo: Callable[[str, str], None],
    root,
    tk,
    bg_deep: str,
    bg_panel: str,
    accent_pink: str,
    text_primary: str,
    t: Callable[[str], str],
    save_presets_dict: Callable[[dict], None],
    refresh_preset_menu: Callable[[], None],
    refresh_ui_lang: Callable[[], None],
) -> None:
    if not presets_dict:
        messagebox_showinfo(t("lbl_preset"), t("msg_no_preset"))
        return

    win = tk.Toplevel(root)
    win.title(t("preset_delete"))
    win.configure(bg=bg_deep)
    win.transient(root)

    tk.Label(
        win,
        text=t("preset_delete"),
        fg=text_primary,
        bg=bg_deep,
        font=("Microsoft YaHei UI", 10),
    ).pack(pady=(12, 6), padx=12)

    lb = tk.Listbox(
        win,
        height=min(12, len(presets_dict)),
        bg=bg_panel,
        fg=text_primary,
        font=("Microsoft YaHei UI", 9),
        selectmode=tk.SINGLE,
    )
    for name in presets_dict:
        lb.insert(tk.END, name)
    lb.pack(padx=12, pady=(0, 8), fill=tk.BOTH, expand=True)

    def do_del():
        delete_preset_do_del_logic(
            listbox=lb,
            presets_dict=presets_dict,
            messagebox_showinfo=messagebox_showinfo,
            save_presets_dict=save_presets_dict,
            refresh_preset_menu=refresh_preset_menu,
            refresh_ui_lang=refresh_ui_lang,
            t=t,
            dialog_win=win,
        )

    btn_text = t("preset_delete").replace("…", "")
    tk.Button(
        win,
        text=btn_text,
        command=do_del,
        bg=bg_panel,
        fg=accent_pink,
        relief=tk.FLAT,
        font=("Microsoft YaHei UI", 9),
        cursor="hand2",
    ).pack(pady=(0, 12), padx=12)
    win.grab_set()


def delete_preset_do_del_logic(
    *,
    listbox,
    presets_dict: dict,
    messagebox_showinfo: Callable[[str, str], None],
    save_presets_dict: Callable[[dict], None],
    refresh_preset_menu: Callable[[], None],
    refresh_ui_lang: Callable[[], None],
    t: Callable[[str], str],
    dialog_win,
) -> None:
    sel = listbox.curselection()
    if not sel:
        messagebox_showinfo(t("lbl_preset"), t("msg_select_preset"))
        return
    name = listbox.get(sel[0])
    presets_dict.pop(name, None)
    save_presets_dict(presets_dict)
    refresh_preset_menu()
    refresh_ui_lang()
    messagebox_showinfo(t("lbl_preset"), t("msg_preset_deleted") % name)
    dialog_win.destroy()


def batch_export_logic(
    *,
    filedialog,
    messagebox_showinfo: Callable[[str, str], None],
    t: Callable[[str], str],
    current_style_get: Callable[[], str],
    current_effect_get: Callable[[], str],
    color_mode_get: Callable[[], bool],
    get_transparent_bg_rgb: Callable[[], tuple | None],
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    pad_to_display: Callable[..., Any],
) -> None:
    paths = filedialog.askopenfilenames(
        title=t("dialog_batch_files"),
        filetypes=[
            (t("filter_images"), "*.png;*.jpg;*.jpeg;*.gif;*.webp;*.bmp;*.tiff;*.tif;*.ico"),
            (t("filter_all"), "*.*"),
        ],
    )
    if not paths:
        return

    out_dir = filedialog.askdirectory(title=t("dialog_batch_dir"))
    if not out_dir:
        return

    style_name = current_style_get()
    chars = CHAR_STYLES.get(style_name, CHAR_STYLES["默认"])
    effect = EFFECTS.get(current_effect_get(), 0)
    color_mode = color_mode_get()
    trans_bg = get_transparent_bg_rgb()
    gw = get_gui_width()
    gh = get_gui_height()
    ok = fail = 0

    for path in paths:
        if not os.path.isfile(path):
            fail += 1
            continue
        try:
            frames, _ = get_animated_frames(path)
            if not frames:
                fail += 1
                continue
            img = frames[0]
            name = os.path.splitext(os.path.basename(path))[0]

            if color_mode:
                lines, colors, cw, ch = _charart_from_pil(
                    img, gw, gh, chars, effect,
                    return_colors=True, transparent_bg=trans_bg,
                )
                padded, padded_colors = pad_to_display(lines, cw, ch, colors)

                txt_path = os.path.join(out_dir, name + ".txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(padded))

                html_path = os.path.join(out_dir, name + ".html")
                html = '<pre style="font-family:Consolas,monospace;background:#281626;color:#fce4ec;">\n'
                for row_idx, line in enumerate(padded):
                    row_colors = (
                        padded_colors[row_idx]
                        if row_idx < len(padded_colors)
                        else []
                    )
                    parts = []
                    for col_idx, ch in enumerate(line):
                        if col_idx < len(row_colors):
                            r, g, b = row_colors[col_idx][:3]
                        else:
                            r, g, b = 128, 128, 128
                        esc = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                        parts.append(f'<span style="color:#{r:02x}{g:02x}{b:02x}">{esc}</span>')
                    html += "".join(parts) + "\n"
                html += "</pre>"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(
                        "<!DOCTYPE html><html><head><meta charset=\"utf-8\"/></head><body>"
                        + html
                        + "</body></html>"
                    )
            else:
                lines, cw, ch = _charart_from_pil(
                    img, gw, gh, chars, effect, transparent_bg=trans_bg,
                )
                padded = pad_to_display(lines, cw, ch)
                txt_path = os.path.join(out_dir, name + ".txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(padded))
            ok += 1
        except Exception:
            fail += 1

    messagebox_showinfo(t("btn_batch"), t("msg_batch_done") % (ok, fail))


def update_scrollbar_visibility_logic(
    *,
    art_text,
    root,
    tk,
    xscroll,
    yscroll,
) -> None:
    try:
        root.update_idletasks()
        content = art_text.get("1.0", tk.END)
        parts = content.split("\n")
        lines = len(parts) if parts else 1
        max_col = max((len(l.rstrip("\r\n")) for l in parts), default=0)
        vw = art_text.cget("width")
        vh = art_text.cget("height")

        if lines > vh:
            yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            yscroll.pack_forget()

        if max_col > vw:
            xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            xscroll.pack_forget()
    except Exception:
        pass


def block_insert_logic(*_args, **_kwargs) -> str:
    return "break"


def block_copy_logic(*_args, **_kwargs) -> str:
    return "break"


def block_select_logic(*_args, **_kwargs) -> str:
    return "break"


def rebuild_var_radiomenu(
    menu,
    tk_end,
    var,
    options: tuple[str, ...],
    i18n_keys: dict[str, str],
    t: Callable[[str], str],
    on_change: Callable[[], None] | None = None,
) -> None:
    """重建 Menubutton 下拉项（透明背景 / 导出底色等）。"""
    menu.delete(0, tk_end)
    for val in options:
        menu.add_radiobutton(
            label=t(i18n_keys[val]),
            variable=var,
            value=val,
            command=on_change,
        )


def update_menubutton_var_label(
    btn,
    var,
    i18n_keys: dict[str, str],
    t: Callable[[str], str],
) -> None:
    val = var.get()
    btn["text"] = t(i18n_keys.get(val, val))


def refresh_ui_lang_logic(
    ui,
    *,
    root,
    t: Callable[[str], str],
    lang_var_get: Callable[[], str],
    drop_overlay_lbl,
    refresh_preset_menu: Callable[[], None],
    update_foot_and_size: Callable[[], None],
    preview_win: list,
    current_path_get: Callable[[], str],
) -> None:
    """ui 为 refresh_ui_lang 函数对象，其上挂载 btn_open 等 widget 引用。"""
    root.title(t("app_title"))

    if hasattr(ui, "lang_btn"):
        ui.lang_btn["text"] = t("lang_" + lang_var_get())

    widget_keys = (
        ("btn_open", "btn_open"),
        ("btn_reset", "btn_reset"),
        ("btn_copy", "btn_copy"),
        ("btn_original", "btn_original"),
        ("btn_export_txt", "btn_export_txt"),
        ("btn_export_html", "btn_export_html"),
        ("btn_export_png", "btn_export_png"),
        ("btn_export_gif", "btn_export_gif"),
        ("btn_batch", "btn_batch"),
        ("btn_follow_author", "btn_follow_author"),
        ("disclaimer_label", "disclaimer"),
        ("lbl_size_preset", "lbl_size_preset"),
        ("lbl_width", "lbl_width"),
        ("lbl_height", "lbl_height"),
        ("lbl_transparent", "lbl_transparent"),
        ("lbl_export_bg", "lbl_export_bg"),
        ("lbl_style", "lbl_style"),
        ("lbl_effect", "lbl_effect"),
        ("cb_color", "lbl_color_mode"),
        ("lbl_speed", "lbl_speed"),
        ("recent_btn", "lbl_recent"),
        ("preset_btn", "lbl_preset"),
        ("lbl_zoom", "lbl_zoom"),
        ("title_label", "title_art"),
    )
    if hasattr(ui, "btn_open"):
        for attr, key in widget_keys:
            if hasattr(ui, attr):
                getattr(ui, attr)["text"] = t(key)

    if drop_overlay_lbl is not None:
        drop_overlay_lbl["text"] = t("drop_hint")

    if hasattr(ui, "trans_menu") and hasattr(ui, "trans_btn"):
        rebuild_var_radiomenu(
            ui.trans_menu,
            ui.tk_end,
            ui.transparent_var,
            ui.transparent_options,
            ui.transparent_i18n,
            t,
        )
        update_menubutton_var_label(
            ui.trans_btn, ui.transparent_var, ui.transparent_i18n, t
        )

    if hasattr(ui, "export_bg_menu") and hasattr(ui, "export_bg_btn"):
        rebuild_var_radiomenu(
            ui.export_bg_menu,
            ui.tk_end,
            ui.export_bg_var,
            ui.export_bg_options,
            ui.export_bg_i18n,
            t,
        )
        update_menubutton_var_label(
            ui.export_bg_btn, ui.export_bg_var, ui.export_bg_i18n, t
        )

    refresh_preset_menu()
    update_foot_and_size()

    win = preview_win[0]
    if win is not None and win.winfo_exists() and current_path_get():
        win.title(t("original_title") + os.path.basename(current_path_get()))


def close_preview_if_open_logic(*, preview_win: list) -> None:
    win = preview_win[0]
    if win is not None and win.winfo_exists():
        win.destroy()


def on_closing_logic(
    *,
    save_recent_paths: Callable[[list], None],
    save_presets_dict: Callable[[dict], None],
    save_last_path: Callable[[str], None],
    recent_paths: list,
    presets_dict: dict,
    current_path_get: Callable[[], str],
    root,
) -> None:
    save_recent_paths(recent_paths)
    save_presets_dict(presets_dict)
    p = current_path_get()
    if p and os.path.isfile(p):
        save_last_path(os.path.abspath(p))
    root.destroy()


def open_author_bilibili_logic() -> None:
    webbrowser.open("https://space.bilibili.com/259516939")
