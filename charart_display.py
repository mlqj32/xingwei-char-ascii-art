# -*- coding: utf-8 -*-
"""显示/填充相关纯函数（对照 charart.pyc line 806-849）。"""
from __future__ import annotations

from typing import Callable

from charart_i18n import DEFAULT_PAD_COLOR


def pad_to_display_static(
    lines: list[str],
    cw: int,
    ch: int,
    gw: int,
    gh: int,
    colors: list | None = None,
    pad_color: tuple[int, int, int] | None = None,
):
    """line 806-826：静态 gw/gh 下居中填充"""
    if pad_color is None:
        pad_color = DEFAULT_PAD_COLOR

    pad_left = (gw - cw) // 2
    pad_right = gw - cw - pad_left
    space_line = " " * gw
    padded = [space_line] * ((gh - ch) // 2)
    padded_colors = [] if colors is not None else None

    if colors is not None and padded_colors is not None:
        padded_colors = [[pad_color] * gw for _ in padded]

    for row_idx, line in enumerate(lines):
        padded.append(" " * pad_left + line + " " * pad_right)
        if colors is not None and padded_colors is not None:
            row_colors = (
                [pad_color] * pad_left
                + list(colors[row_idx])
                + [pad_color] * pad_right
            )
            padded_colors.append(row_colors)

    while len(padded) < gh:
        padded.append(space_line)
        if colors is not None and padded_colors is not None:
            padded_colors.append([pad_color] * gw)

    if colors is not None:
        return padded, padded_colors
    return padded


def pad_to_display(
    lines: list[str],
    cw: int,
    ch: int,
    colors: list | None,
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    pad_color: tuple[int, int, int] | None = None,
):
    """line 828-849：按当前 GUI 尺寸居中填充"""
    if pad_color is None:
        pad_color = DEFAULT_PAD_COLOR

    gw = get_gui_width()
    gh = get_gui_height()
    pad_left = (gw - cw) // 2
    pad_top = (gh - ch) // 2
    pad_right = gw - cw - pad_left
    space_line = " " * gw
    padded = [space_line] * pad_top
    padded_colors: list = []

    if colors is not None:
        padded_colors = [[pad_color] * gw for _ in range(pad_top)]

    for row_idx, line in enumerate(lines):
        padded.append(" " * pad_left + line + " " * pad_right)
        if colors is not None:
            row_colors = (
                [pad_color] * pad_left
                + list(colors[row_idx])
                + [pad_color] * pad_right
            )
            padded_colors.append(row_colors)

    while len(padded) < gh:
        padded.append(space_line)
        if colors is not None:
            padded_colors.append([pad_color] * gw)

    if colors is not None:
        return padded, padded_colors
    return padded


def stop_animation_logic(
    anim_after_id: list,
    anim_frames_data: list,
    anim_frames_colors: list,
    anim_durations: list,
    root_after_cancel: Callable[[object], None],
) -> None:
    """line 795-801"""
    if anim_after_id[0] is not None:
        root_after_cancel(anim_after_id[0])
        anim_after_id[0] = None
    anim_frames_data.clear()
    anim_frames_colors.clear()
    anim_durations.clear()
