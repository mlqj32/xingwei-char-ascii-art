# -*- coding: utf-8 -*-
"""导出与剪贴板。"""
from __future__ import annotations

from typing import Any, Callable

from charart_core import _render_art_to_image, _rgba_frames_to_gif_p
from charart_i18n import EXPORT_BG_OPTIONS


def get_art_text_logic(
    *,
    last_shown_code: list,
    anim_frames_data: list,
    art_text_get: Callable[[str, str], str],
    tk_end: Any,
) -> str:
    """line 1181-1187"""
    if last_shown_code[0] is not None:
        return last_shown_code[0]
    if anim_frames_data:
        return "\n".join(anim_frames_data[0])
    return art_text_get("1.0", tk_end)


def get_art_html_logic(
    *,
    last_shown_padded: list,
    last_shown_colors: list,
) -> str | None:
    """line 1189-1204"""
    padded = last_shown_padded[0]
    colors = last_shown_colors[0]
    if not padded or not colors or len(padded) != len(colors):
        return None

    lines_html: list[str] = []
    for row_idx, line in enumerate(padded):
        row_colors = colors[row_idx] if row_idx < len(colors) else []
        parts: list[str] = []
        for col_idx, ch in enumerate(line):
            if col_idx < len(row_colors):
                r, g, b = row_colors[col_idx][:3]
            else:
                r, g, b = 128, 128, 128
            esc = ch.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(f'<span style="color:#{r:02x}{g:02x}{b:02x}">{esc}</span>')
        lines_html.append("".join(parts))

    return (
        '<pre style="font-family:Consolas,monospace;background:#281626;'
        f'color:#fce4ec;margin:0;padding:8px;">\n'
        + "\n".join(lines_html)
        + "\n</pre>"
    )


def copy_art_logic(
    *,
    get_art_html: Callable[[], str | None],
    get_art_text: Callable[[], str],
    root_clipboard_clear: Callable[[], None],
    root_clipboard_append: Callable[[str], None],
    messagebox_showinfo: Callable[[str, str], None],
    messagebox_showwarning: Callable[[str, str], None],
    t: Callable[[str], str],
) -> None:
    """line 1206-1220"""
    html = get_art_html()
    if html:
        root_clipboard_clear()
        root_clipboard_append(html)
        messagebox_showinfo(t("btn_copy"), t("msg_copied_html"))
        return
    text = get_art_text()
    if text.strip():
        root_clipboard_clear()
        root_clipboard_append(text)
        messagebox_showinfo(t("btn_copy"), t("msg_copied"))
        return
    messagebox_showwarning(t("btn_copy"), t("msg_nothing_copy"))


def export_txt_logic(
    *,
    get_art_text: Callable[[], str],
    filedialog_asksaveasfilename: Callable[..., str],
    messagebox_showwarning: Callable[[str, str], None],
    messagebox_showinfo: Callable[[str, str], None],
    messagebox_showerror: Callable[[str, str], None],
    t: Callable[[str], str],
) -> None:
    """line 1222-1239"""
    text = get_art_text()
    if not text.strip():
        messagebox_showwarning(t("btn_export_txt"), t("msg_nothing_export"))
        return
    path = filedialog_asksaveasfilename(
        title=t("dialog_export_txt"),
        defaultextension=".txt",
        filetypes=[(t("filter_txt"), "*.txt"), (t("filter_all"), "*.*")],
    )
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox_showinfo(t("btn_export_txt"), t("msg_export_ok") + path)
    except Exception as e:
        messagebox_showerror(t("btn_export_txt"), t("msg_export_fail") + str(e))


def export_html_logic(
    *,
    get_art_html: Callable[[], str | None],
    filedialog_asksaveasfilename: Callable[..., str],
    messagebox_showwarning: Callable[[str, str], None],
    messagebox_showinfo: Callable[[str, str], None],
    messagebox_showerror: Callable[[str, str], None],
    t: Callable[[str], str],
) -> None:
    """line 1241-1260"""
    html = get_art_html()
    if not html:
        messagebox_showwarning(t("btn_export_html"), t("msg_no_color"))
        return
    path = filedialog_asksaveasfilename(
        title=t("dialog_export_html"),
        defaultextension=".html",
        filetypes=[(t("filter_html"), "*.html"), (t("filter_all"), "*.*")],
    )
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html><head><meta charset=\"utf-8\"/>")
            f.write("<title>ASCII Art</title></head><body>\n")
            f.write(html)
            f.write("\n</body></html>")
        messagebox_showinfo(t("btn_export_html"), t("msg_export_ok") + path)
    except Exception as e:
        messagebox_showerror(t("btn_export_html"), t("msg_export_fail") + str(e))


def export_png_logic(
    *,
    last_shown_padded: list,
    last_shown_colors: list,
    export_bg_var_get: Callable[[], str],
    filedialog_asksaveasfilename: Callable[..., str],
    messagebox_showwarning: Callable[[str, str], None],
    messagebox_showinfo: Callable[[str, str], None],
    messagebox_showerror: Callable[[str, str], None],
    t: Callable[[str], str],
    export_bg_options: dict | None = None,
) -> None:
    """line 1262-1281"""
    export_bg_options = export_bg_options or EXPORT_BG_OPTIONS
    padded = last_shown_padded[0]
    if not padded:
        messagebox_showwarning(t("btn_export_png"), t("msg_nothing_export"))
        return
    path = filedialog_asksaveasfilename(
        title=t("dialog_export_png"),
        defaultextension=".png",
        filetypes=[(t("filter_png"), "*.png"), (t("filter_all"), "*.*")],
    )
    if not path:
        return
    try:
        bg = export_bg_options.get(export_bg_var_get(), (0, 0, 0))
        img = _render_art_to_image(padded, last_shown_colors[0], bg)
        img.save(path, format="PNG")
        messagebox_showinfo(t("btn_export_png"), t("msg_export_ok") + path)
    except Exception as e:
        messagebox_showerror(t("btn_export_png"), t("msg_export_fail") + str(e))


def export_gif_logic(
    *,
    anim_frames_data: list,
    anim_frames_colors: list,
    anim_durations: list,
    last_shown_padded: list,
    last_shown_colors: list,
    export_bg_var_get: Callable[[], str],
    filedialog_asksaveasfilename: Callable[..., str],
    messagebox_showwarning: Callable[[str, str], None],
    messagebox_showinfo: Callable[[str, str], None],
    messagebox_showerror: Callable[[str, str], None],
    t: Callable[[str], str],
    export_bg_options: dict | None = None,
) -> None:
    """line 1283-1333"""
    export_bg_options = export_bg_options or EXPORT_BG_OPTIONS
    bg = export_bg_options.get(export_bg_var_get(), (0, 0, 0))
    frames_img: list = []
    durations_ms: list[int] = []

    if anim_frames_data:
        for i, padded in enumerate(anim_frames_data):
            colors = (
                anim_frames_colors[i]
                if i < len(anim_frames_colors)
                else None
            )
            frames_img.append(_render_art_to_image(padded, colors, bg))
            d = anim_durations[i] if i < len(anim_durations) else 100
            durations_ms.append(max(20, int(d)))
        if not frames_img:
            messagebox_showwarning(t("btn_export_gif"), t("msg_nothing_export"))
            return
    else:
        padded = last_shown_padded[0]
        if not padded:
            messagebox_showwarning(t("btn_export_gif"), t("msg_nothing_export"))
            return
        frames_img = [_render_art_to_image(padded, last_shown_colors[0], bg)]
        durations_ms = [100]

    path = filedialog_asksaveasfilename(
        title=t("dialog_export_gif"),
        defaultextension=".gif",
        filetypes=[(t("filter_gif"), "*.gif"), (t("filter_all"), "*.*")],
    )
    if not path:
        return
    try:
        append = frames_img[1:] if len(frames_img) > 1 else []
        if bg is None:
            frames_p, durations_ms = _rgba_frames_to_gif_p(frames_img, durations_ms)
            append_p = frames_p[1:] if len(frames_p) > 1 else []
            frames_p[0].save(
                path,
                save_all=True,
                append_images=append_p,
                duration=durations_ms,
                loop=0,
                transparency=0,
            )
        else:
            frames_img[0].save(
                path,
                save_all=True,
                append_images=append,
                duration=durations_ms,
                loop=0,
            )
        messagebox_showinfo(t("btn_export_gif"), t("msg_export_ok") + path)
    except Exception as e:
        messagebox_showerror(t("btn_export_gif"), t("msg_export_fail") + str(e))
