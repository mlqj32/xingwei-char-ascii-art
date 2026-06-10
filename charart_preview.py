# -*- coding: utf-8 -*-
"""预览窗口：原图 / 动图预览（line 660-791）。"""
from __future__ import annotations

import os
from typing import Any, Callable

from charart_core import Image, get_animated_frames

PREVIEW_MAX_W = 400


def load_preview_photo_logic(path: str, max_w: int = PREVIEW_MAX_W, *, ImageTk) -> Any:
    """line 660-676"""
    img = Image.open(path)
    if img.mode != "RGBA":
        img = img.convert("RGB")
        w, h = img.size
        if w > max_w:
            scale = max_w / w
            img = img.resize(
                (max_w, int(h * scale)),
                Image.Resampling.LANCZOS,
            )
        return ImageTk.PhotoImage(img)

    w, h = img.size
    if w > max_w:
        scale = max_w / w
        img = img.resize(
            (max_w, int(h * scale)),
            Image.Resampling.LANCZOS,
        )
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    return ImageTk.PhotoImage(bg)


def pil_to_photo_logic(img_pil, max_w: int = PREVIEW_MAX_W, *, ImageTk) -> Any:
    """line 678-692"""
    if img_pil.mode != "RGBA":
        img = img_pil.convert("RGB")
    else:
        img = img_pil

    w, h = img.size
    if w > max_w:
        scale = max_w / w
        img = img.resize(
            (max_w, int(h * scale)),
            Image.Resampling.LANCZOS,
        )

    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg

    return ImageTk.PhotoImage(img)


def stop_preview_gif_logic(
    preview_after_id: list,
    preview_photos: list,
    preview_win: list,
) -> None:
    """line 694-702"""
    if preview_after_id[0] is not None:
        try:
            win = preview_win[0]
            if win and win.winfo_exists():
                win.after_cancel(preview_after_id[0])
        except Exception:
            pass
        preview_after_id[0] = None
    preview_photos.clear()


def preview_gif_next_logic(
    win,
    lbl,
    frame_idx: int,
    durations: list,
    max_w: int = PREVIEW_MAX_W,
    *,
    preview_photos: list,
    preview_after_id: list,
    preview_gif_next: Callable[..., None],
) -> None:
    """line 704-712"""
    if not win.winfo_exists() or not preview_photos:
        return

    lbl.configure(image=preview_photos[frame_idx])
    next_idx = (frame_idx + 1) % len(preview_photos)
    delay = durations[next_idx] if next_idx < len(durations) else 100
    delay = max(20, int(delay))
    preview_after_id[0] = win.after(
        delay, preview_gif_next, win, lbl, next_idx, durations, max_w
    )


def update_preview_window_logic(
    *,
    preview_win: list,
    preview_label: list,
    current_path_get: Callable[[], str],
    stop_preview_gif: Callable[[], None],
    pil_to_photo: Callable[..., Any],
    load_preview_photo: Callable[[str], Any],
    preview_gif_next: Callable[..., None],
    preview_photos: list,
    preview_photo: list,
    t: Callable[[str], str],
) -> None:
    """line 714-736"""
    win = preview_win[0]
    lbl = preview_label[0]
    if win is None or lbl is None or not win.winfo_exists():
        return

    path = current_path_get()
    if not path or not os.path.isfile(path):
        return

    stop_preview_gif()
    try:
        frames, durations = get_animated_frames(path)
        if len(frames) > 1:
            preview_photos.extend([pil_to_photo(f) for f in frames])
            if not preview_photos:
                return
            dur = durations if durations else [100] * len(preview_photos)
            preview_gif_next(win, lbl, 0, dur)
        else:
            photo = load_preview_photo(path)
            preview_photo[0] = photo
            lbl.configure(image=photo)

        win.title(t("original_title") + os.path.basename(path))
    except Exception:
        return


def preview_on_close_logic(
    *,
    stop_preview_gif: Callable[[], None],
    preview_win: list,
    preview_label: list,
    preview_photo: list,
    win,
) -> None:
    """line 765-770"""
    stop_preview_gif()
    preview_win[0] = None
    preview_label[0] = None
    preview_photo[0] = None
    win.destroy()


def show_original_logic(
    *,
    current_path_get: Callable[[], str],
    messagebox_showinfo: Callable[[str, str], None],
    t: Callable[[str], str],
    preview_win: list,
    update_preview_window: Callable[[], None],
    stop_preview_gif: Callable[[], None],
    pil_to_photo: Callable[..., Any],
    load_preview_photo: Callable[[str], Any],
    preview_photos: list,
    preview_photo: list,
    tk,
    root,
    bg_deep: str,
    bg_panel: str,
    preview_gif_next: Callable[..., None],
    messagebox_showerror: Callable[[str, str], None],
) -> None:
    """line 738-791"""
    path = current_path_get()
    if not path or not os.path.isfile(path):
        messagebox_showinfo(t("btn_original"), t("msg_original_first"))
        return

    win = preview_win[0]
    if win is not None and win.winfo_exists():
        update_preview_window()
        win.lift()
        win.focus_force()
        return

    try:
        frames, durations = get_animated_frames(path)
        if len(frames) > 1:
            preview_photos.clear()
            preview_photos.extend([pil_to_photo(f) for f in frames])
            if not preview_photos:
                raise RuntimeError("无法加载动图帧")
            photo = preview_photos[0]
        else:
            photo = load_preview_photo(path)
            preview_photo[0] = photo

        new_win = tk.Toplevel(root)
        new_win.title(t("original_title") + os.path.basename(path))
        new_win.configure(bg=bg_deep)
        new_win.resizable(True, True)
        lbl = tk.Label(new_win, image=photo, bg=bg_panel)
        lbl.pack(padx=12, pady=12)

        def on_close():
            preview_on_close_logic(
                stop_preview_gif=stop_preview_gif,
                preview_win=preview_win,
                preview_label=preview_label,
                preview_photo=preview_photo,
                win=new_win,
            )

        new_win.protocol("WM_DELETE_WINDOW", on_close)
        preview_win[0] = new_win
        preview_label[0] = lbl

        new_win.update_idletasks()
        rx, ry = root.winfo_x(), root.winfo_y()
        rw, rh = root.winfo_width(), root.winfo_height()
        ww, wh = new_win.winfo_reqwidth(), new_win.winfo_reqheight()
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        px = rx + rw + 20
        py = ry
        if px + ww > sw:
            px = max(20, rx - ww - 20)
        if py + wh > sh:
            py = max(20, sh - wh - 20)
        if py < 0:
            py = 20
        new_win.geometry(f"+{px}+{py}")

        if len(frames) > 1 and preview_photos:
            dur = durations if durations else [100] * len(preview_photos)
            preview_gif_next(new_win, lbl, 0, dur)
    except Exception as e:
        messagebox_showerror("Error", t("msg_error_load") + str(e))
