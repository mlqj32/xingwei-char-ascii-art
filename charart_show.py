# -*- coding: utf-8 -*-
"""主画布显示与动图帧播放。"""
from __future__ import annotations

from typing import Any, Callable


def show_code_logic(
    code_str: str | None,
    padded_keep,
    *,
    last_shown_code: list,
    last_shown_padded: list,
    last_shown_colors: list,
    art_text,
    tk,
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    root,
    update_scrollbar_visibility: Callable[[], None],
) -> None:
    """line 852-868"""
    last_shown_code[0] = code_str
    last_shown_padded[0] = padded_keep
    last_shown_colors[0] = None

    art_text.configure(state=tk.NORMAL)
    art_text.delete("1.0", tk.END)
    if code_str is not None:
        art_text.insert(tk.END, code_str)
    art_text.configure(state=tk.DISABLED)

    parts = code_str.split("\n") if code_str else []
    code_lines = len(parts) if parts else 1
    code_max_col = max((len(l.rstrip("\r\n")) for l in parts), default=0)
    fit_w = min(max(get_gui_width() + 1, code_max_col + 1), 140)
    fit_h = min(max(get_gui_height() + 1, code_lines + 1), 90)
    art_text.configure(width=fit_w, height=fit_h)
    root.after(50, update_scrollbar_visibility)


def show_padded_logic(
    padded: list[str],
    padded_colors: list | None,
    *,
    last_shown_code: list,
    last_shown_padded: list,
    last_shown_colors: list,
    art_text,
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    _pad_color: tuple[int, int, int],
    tk,
    root,
    update_scrollbar_visibility: Callable[[], None],
) -> None:
    """line 870-916"""
    last_shown_code[0] = None
    last_shown_padded[0] = padded
    last_shown_colors[0] = padded_colors

    art_text.configure(
        width=get_gui_width() + 1,
        height=get_gui_height() + 1,
    )

    saved_yview = saved_xview = None
    try:
        saved_yview = art_text.yview()
        saved_xview = art_text.xview()
    except Exception:
        saved_yview = saved_xview = None

    art_text.configure(state=tk.NORMAL)
    art_text.delete("1.0", tk.END)

    if padded_colors is None:
        art_text.insert(tk.END, "\n".join(padded))
    else:
        color_to_tag: dict[tuple, str] = {}
        tag_id = [0]

        def tag_for(rgb: tuple) -> str:
            k = rgb
            if k not in color_to_tag:
                name = "col_%d" % tag_id[0]
                tag_id[0] += 1
                art_text.tag_configure(
                    name,
                    foreground="#%02x%02x%02x" % (rgb[0], rgb[1], rgb[2]),
                )
                color_to_tag[k] = name
            return color_to_tag[k]

        for row_idx, line in enumerate(padded):
            row_colors = padded_colors[row_idx]
            for col_idx, ch in enumerate(line):
                rgb = row_colors[col_idx] if col_idx < len(row_colors) else _pad_color
                art_text.insert(tk.END, ch, tag_for(rgb))
            if row_idx < len(padded) - 1:
                art_text.insert(tk.END, "\n")

    if saved_yview is not None and saved_xview is not None:
        try:
            art_text.yview_moveto(saved_yview[0])
            art_text.xview_moveto(saved_xview[0])
        except Exception:
            pass

    art_text.configure(state=tk.DISABLED)
    root.after(50, update_scrollbar_visibility)


def play_next_frame_logic(
    *,
    anim_frames_data: list,
    anim_frames_colors: list,
    anim_index: list,
    anim_durations: list,
    anim_speed: list,
    anim_after_id: list,
    show_padded: Callable[..., None],
    play_next_frame: Callable[[], None],
    root,
) -> None:
    """line 918-927"""
    if not anim_frames_data:
        return

    idx = anim_index[0]
    if anim_frames_colors:
        padded_colors = anim_frames_colors[idx]
    else:
        padded_colors = None

    show_padded(anim_frames_data[idx], padded_colors)

    n = len(anim_frames_data)
    anim_index[0] = (idx + 1) % n

    if anim_index[0] < len(anim_durations):
        delay_ms = anim_durations[anim_index[0]]
    else:
        delay_ms = 100

    delay_ms = max(20, int(delay_ms / anim_speed[0]))
    anim_after_id[0] = root.after(delay_ms, play_next_frame)
