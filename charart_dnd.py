# -*- coding: utf-8 -*-
"""拖拽打开图片。"""
from __future__ import annotations

import os
from typing import Callable


def show_drop_overlay_logic(
    *,
    drop_overlay,
    drop_overlay_lbl,
    t: Callable[[str], str],
) -> None:
    """line 1864-1867"""
    drop_overlay_lbl["text"] = t("drop_hint")
    drop_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)


def hide_drop_overlay_logic(*, drop_overlay) -> None:
    """line 1869-1870"""
    drop_overlay.place_forget()


def on_drop_art_logic(
    *,
    event_data: str,
    hide_drop_overlay: Callable[[], None],
    open_image: Callable[[str], None],
) -> str:
    """line 1960-1965"""
    path = event_data.strip().strip("{}")
    hide_drop_overlay()
    if path and os.path.isfile(path):
        open_image(path)
    return "copy"


def on_drop_enter_art_logic(*, show_drop_overlay: Callable[[], None]) -> str:
    """line 1966-1968"""
    show_drop_overlay()
    return "copy"


def on_drop_leave_art_logic(*, hide_drop_overlay: Callable[[], None]) -> None:
    """line 1969-1970"""
    hide_drop_overlay()


def on_drop_windnd_logic(
    *,
    files,
    open_image: Callable[[str], None],
) -> None:
    """line 1978-1982"""
    if not files:
        return
    first = files[0]
    path = first if isinstance(first, str) else first.decode("utf-8", errors="replace")
    if path and os.path.isfile(path):
        open_image(path)


def on_drop_root_logic(
    *,
    event_data: str,
    open_image: Callable[[str], None],
) -> None:
    """line 1955-1958（与 on_drop_art 类似，无 overlay）"""
    path = event_data.strip().strip("{}")
    if path and os.path.isfile(path):
        open_image(path)
