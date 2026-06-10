# -*- coding: utf-8 -*-
"""
从 charart.pyc 反汇编还原的 GUI 逻辑（charart.py line 421+）。

完整 Tk 界面布局（工具栏/导出/动画等，约 421-2015 行）仍在 charart.pyc；
本文件还原：
  - 配置读写（recent / presets / last_path）
  - open_image 流程（632-658）
  - refresh_art 核心流程（996-1175）
  - run_gui 入口：注入还原算法后调用原版 GUI
"""
from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path
from typing import Any, Callable

from charart_core import (
    CHAR_STYLES,
    CODE_STYLES,
    EFFECTS,
    _charart_from_pil,
    art_to_code,
    generate_charart,
    get_animated_frames,
)
from charart_display import pad_to_display_static
from charart_i18n import DEFAULT_PAD_COLOR

RECENT_MAX = 10
ROOT_DIR = Path(__file__).resolve().parent
I18N_PATH = ROOT_DIR / "docs" / "module_constants.json"


def _config_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return ROOT_DIR


def _t(lang: str, key: str) -> str:
    """line 225"""
    if I18N_PATH.is_file():
        data = json.loads(I18N_PATH.read_text(encoding="utf-8"))
        d = data.get("I18N", {}).get(key, {})
        if isinstance(d, dict):
            return d.get(lang, d.get("zh", key))
    return key


def load_recent_paths(recent_file: Path | None = None) -> list[str]:
    """line 442-449"""
    recent_file = recent_file or _config_dir() / ".charart_recent"
    if not recent_file.is_file():
        return []
    try:
        with recent_file.open("r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and os.path.isfile(line.strip())
            ]
    except Exception:
        return []


def save_recent_paths(paths: list[str], recent_file: Path | None = None) -> None:
    """line 451-457"""
    recent_file = recent_file or _config_dir() / ".charart_recent"
    try:
        with recent_file.open("w", encoding="utf-8") as f:
            for p in paths[:RECENT_MAX]:
                f.write(p + "\n")
    except Exception:
        pass


def load_presets_dict(presets_file: Path | None = None) -> dict:
    """line 459-466"""
    presets_file = presets_file or _config_dir() / ".charart_presets.json"
    if not presets_file.is_file():
        return {}
    try:
        with presets_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_presets_dict(data: dict, presets_file: Path | None = None) -> None:
    """line 468-473"""
    presets_file = presets_file or _config_dir() / ".charart_presets.json"
    try:
        with presets_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_last_path(last_path_file: Path | None = None) -> str:
    """line 475-483"""
    last_path_file = last_path_file or _config_dir() / ".charart_last_path"
    if not last_path_file.is_file():
        return ""
    try:
        return last_path_file.read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def save_last_path(path: str, last_path_file: Path | None = None) -> None:
    """line 485-490"""
    last_path_file = last_path_file or _config_dir() / ".charart_last_path"
    try:
        last_path_file.write_text(path, encoding="utf-8")
    except Exception:
        pass


def refresh_art_logic(
    *,
    path: str,
    current_path_get: Callable[[], str] | None = None,
    current_style_get: Callable[[], str],
    current_effect_get: Callable[[], str],
    color_mode_get: Callable[[], bool],
    get_gui_width: Callable[[], int],
    get_gui_height: Callable[[], int],
    get_transparent_bg_rgb: Callable[[], tuple[int, int, int]],
    stop_animation: Callable[[], None],
    pad_to_display: Callable[..., Any],
    show_code: Callable[..., None],
    show_padded: Callable[..., None],
    show_progress_determinate: Callable[[int], None] | None = None,
    show_progress_indeterminate: Callable[[], None] | None = None,
    close_progress: Callable[[], None] | None = None,
    update_progress: Callable[[int, int], None] | None = None,
    play_next_frame: Callable[[], None] | None = None,
    update_foot_and_size: Callable[[], None] | None = None,
    update_preview_window: Callable[[], None] | None = None,
    messagebox_showerror: Callable[[str, str], None] | None = None,
    anim_frames_data: list | None = None,
    anim_frames_colors: list | None = None,
    anim_durations: list | None = None,
    anim_index: list | None = None,
    root_update: Callable[[], None] | None = None,
    root_after: Callable[[int, Callable[[], None]], Any] | None = None,
    pad_color: tuple[int, int, int] = DEFAULT_PAD_COLOR,
    large_threshold: int = 10000,
) -> None:
    """
    line 996-1175：刷新字符画（静态 / 多帧 / 大图异步）。
    回调由原版 run_gui 闭包注入；此处为可读化还原。
    """
    if not path or not os.path.isfile(path):
        if path and messagebox_showerror:
            messagebox_showerror("Error", "msg_error_file")
        return

    stop_animation()
    style_name = current_style_get()
    chars = CHAR_STYLES.get(style_name, CHAR_STYLES["默认"])
    effect = EFFECTS.get(current_effect_get(), 0)
    color_mode = color_mode_get() if color_mode_get else False

    frames, durations = get_animated_frames(path)

    # --- 动图且帧数 > 1 ---
    if len(frames) > 1:
        if anim_frames_data is not None:
            anim_frames_data.clear()
        if anim_frames_colors is not None:
            anim_frames_colors.clear()
        if anim_durations is not None:
            anim_durations.clear()

        gw, gh = get_gui_width(), get_gui_height()
        trans_bg = get_transparent_bg_rgb()

        if len(frames) > 30 and show_progress_determinate and root_update:
            total = len(frames)
            captured_path = path

            def _pad_static(lines, cw, ch, colors=None):
                return pad_to_display_static(
                    lines, cw, ch, gw, gh, colors, pad_color,
                )

            def worker():
                local_data, local_colors, local_durs = [], [], []
                try:
                    for img in frames:
                        if color_mode:
                            lines, colors, cw, ch = _charart_from_pil(
                                img, gw, gh, chars, effect,
                                return_colors=True, transparent_bg=trans_bg,
                            )
                            if lines:
                                padded, padded_colors = _pad_static(lines, cw, ch, colors)
                                local_data.append(padded)
                                local_colors.append(padded_colors)
                        else:
                            lines, cw, ch = _charart_from_pil(
                                img, gw, gh, chars, effect, transparent_bg=trans_bg,
                            )
                            if lines:
                                local_data.append(_pad_static(lines, cw, ch))
                        if update_progress:
                            update_progress(len(local_data), total)
                    if durations:
                        local_durs = list(durations)
                    else:
                        local_durs = [100] * len(local_data)
                except Exception:
                    def on_err():
                        if close_progress:
                            close_progress()
                        if messagebox_showerror:
                            messagebox_showerror("Error", "msg_error_gen")

                    if root_after:
                        root_after(0, on_err)
                    elif close_progress:
                        close_progress()
                    return

                def apply_on_main():
                    if current_path_get and current_path_get() != captured_path:
                        return
                    if close_progress:
                        close_progress()
                    if anim_frames_data is not None:
                        anim_frames_data.clear()
                        anim_frames_data.extend(local_data)
                    if anim_frames_colors is not None:
                        anim_frames_colors.clear()
                        if local_colors:
                            anim_frames_colors.extend(local_colors)
                    if anim_durations is not None:
                        anim_durations.clear()
                        anim_durations.extend(local_durs)
                    if anim_frames_data:
                        if anim_index is not None:
                            anim_index[0] = 0
                        if style_name in CODE_STYLES:
                            show_code(
                                art_to_code(anim_frames_data[0], style_name),
                                padded_keep=anim_frames_data[0],
                            )
                        elif play_next_frame:
                            play_next_frame()
                    if update_foot_and_size:
                        update_foot_and_size()
                    if update_preview_window:
                        update_preview_window()

                if root_after:
                    root_after(0, apply_on_main)
                else:
                    apply_on_main()

            if show_progress_determinate:
                show_progress_determinate(len(frames))
            if root_update:
                root_update()
            threading.Thread(target=worker, daemon=True).start()
            return

        for img in frames:
            trans_bg = get_transparent_bg_rgb()
            if color_mode:
                lines, colors, cw, ch = _charart_from_pil(
                    img, gw, gh, chars, effect,
                    return_colors=True, transparent_bg=trans_bg,
                )
                if lines and anim_frames_data is not None:
                    padded, padded_colors = pad_to_display(lines, cw, ch, colors)
                    anim_frames_data.append(padded)
                    if anim_frames_colors is not None:
                        anim_frames_colors.append(padded_colors)
            else:
                lines, cw, ch = _charart_from_pil(
                    img, gw, gh, chars, effect, transparent_bg=trans_bg,
                )
                if lines and anim_frames_data is not None:
                    anim_frames_data.append(pad_to_display(lines, cw, ch))

        if anim_durations is not None:
            if durations:
                anim_durations.extend(durations)
            elif anim_frames_data:
                anim_durations.extend([100] * len(anim_frames_data))

        if anim_frames_data:
            if anim_index is not None:
                anim_index[0] = 0
            if style_name in CODE_STYLES:
                show_code(
                    art_to_code(anim_frames_data[0], style_name),
                    padded_keep=anim_frames_data[0],
                )
            elif play_next_frame:
                play_next_frame()
        if update_foot_and_size:
            update_foot_and_size()
        if update_preview_window:
            update_preview_window()
        return

    # --- 静态图 ---
    gw, gh = get_gui_width(), get_gui_height()
    trans_bg = get_transparent_bg_rgb()

    if gw * gh > large_threshold and show_progress_indeterminate and root_update:
        captured_path = path

        def _pad_static(lines, cw, ch, colors=None):
            return pad_to_display_static(
                lines, cw, ch, gw, gh, colors, pad_color,
            )

        def worker_static():
            padded = None
            padded_colors = None
            try:
                from PIL import Image
                img = Image.open(path).convert("RGBA")
                if color_mode:
                    lines, colors, cw, ch = _charart_from_pil(
                        img, gw, gh, chars, effect,
                        return_colors=True, transparent_bg=trans_bg,
                    )
                    if lines:
                        padded, padded_colors = _pad_static(lines, cw, ch, colors)
                else:
                    lines, cw, ch = _charart_from_pil(
                        img, gw, gh, chars, effect, transparent_bg=trans_bg,
                    )
                    if lines:
                        padded = _pad_static(lines, cw, ch)
            except Exception:
                def on_err():
                    if close_progress:
                        close_progress()
                    if messagebox_showerror:
                        messagebox_showerror("Error", "msg_error_gen")

                if root_after:
                    root_after(0, on_err)
                elif close_progress:
                    close_progress()
                return

            def apply_on_main():
                if current_path_get and current_path_get() != captured_path:
                    return
                if close_progress:
                    close_progress()
                if not padded:
                    if messagebox_showerror:
                        messagebox_showerror("Error", "msg_error_gen")
                    return
                if style_name in CODE_STYLES:
                    show_code(art_to_code(padded, style_name), padded_keep=padded)
                elif padded_colors is not None:
                    show_padded(padded, padded_colors)
                else:
                    show_padded(padded)
                if update_foot_and_size:
                    update_foot_and_size()
                if update_preview_window:
                    update_preview_window()

            if root_after:
                root_after(0, apply_on_main)
            else:
                apply_on_main()

        show_progress_indeterminate()
        root_update()
        threading.Thread(target=worker_static, daemon=True).start()
        return

    try:
        if color_mode:
            from PIL import Image
            img = Image.open(path).convert("RGBA")
            lines, colors, cw, ch = _charart_from_pil(
                img, gw, gh, chars, effect,
                return_colors=True, transparent_bg=trans_bg,
            )
        else:
            lines, cw, ch = generate_charart(
                path, gw, gh, chars, effect, transparent_bg=trans_bg,
            )
            colors = None
    except Exception:
        lines, colors, cw, ch = None, None, 0, 0

    if not lines:
        if messagebox_showerror:
            messagebox_showerror("Error", "msg_error_gen")
        return

    if color_mode and colors is not None:
        padded, padded_colors = pad_to_display(lines, cw, ch, colors)
        if style_name in CODE_STYLES:
            show_code(art_to_code(padded, style_name), padded_keep=padded)
        else:
            show_padded(padded, padded_colors)
    else:
        padded = pad_to_display(lines, cw, ch)
        if style_name in CODE_STYLES:
            show_code(art_to_code(padded, style_name), padded_keep=padded)
        else:
            show_padded(padded)

    if update_foot_and_size:
        update_foot_and_size()
    if update_preview_window:
        update_preview_window()


def open_image_logic(
    *,
    path_from_dialog: str | None,
    filedialog_askopenfilename: Callable[..., str],
    current_path_set: Callable[[str], None],
    recent_paths: list[str],
    save_last_path_fn: Callable[[str], None],
    save_recent_paths_fn: Callable[[list[str]], None],
    refresh_recent_menu: Callable[[], None],
    refresh_art_fn: Callable[[], None],
    t: Callable[[str], str],
) -> None:
    """line 632-658：打开图片并刷新"""
    path = path_from_dialog
    if not path:
        path = filedialog_askopenfilename(
            title=t("dialog_open"),
            filetypes=[
                (t("filter_images"), "*.png;*.jpg;*.jpeg;*.gif;*.webp;*.bmp;*.tiff;*.tif;*.ico"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg;*.jpeg"),
                ("GIF", "*.gif"),
                ("WebP", "*.webp"),
                ("BMP", "*.bmp"),
                (t("filter_all"), "*.*"),
            ],
        )
    if not path or not os.path.isfile(path):
        return

    current_path_set(path)
    path_abs = os.path.abspath(path)
    save_last_path_fn(path_abs)
    if path_abs in recent_paths:
        recent_paths.remove(path_abs)
    recent_paths.insert(0, path_abs)
    del recent_paths[RECENT_MAX:]
    save_recent_paths_fn(recent_paths)
    refresh_recent_menu()
    refresh_art_fn()


def _replace_closure_var(frame, varname: str, new_value) -> None:
    """替换 run_gui 栈帧内所有共享 varname 的闭包 cell。"""
    seen_cells = set()
    for obj in list(frame.f_locals.values()):
        if not callable(obj) or not getattr(obj, "__closure__", None):
            continue
        freevars = obj.__code__.co_freevars
        if varname not in freevars:
            continue
        idx = freevars.index(varname)
        cell = obj.__closure__[idx]
        if id(cell) in seen_cells:
            continue
        seen_cells.add(id(cell))
        cell.cell_contents = new_value


def _patch_widget_commands(widget, old_cb, new_cb) -> None:
    """Tk 按钮 command= 在绑定时保存函数引用，需遍历控件树替换。"""
    try:
        for child in widget.winfo_children():
            _patch_widget_commands(child, old_cb, new_cb)
    except Exception:
        pass
    try:
        cmd = widget.cget("command")
        if callable(cmd) and cmd is old_cb:
            widget.configure(command=new_cb)
    except Exception:
        pass


REFRESH_ART_HOOK_APPLIED = False
_HOOK_DEBUG = Path(os.environ.get("CHARART_HOOK_DEBUG", "")) if os.environ.get("CHARART_HOOK_DEBUG") else None


def _debug_hook(msg: str) -> None:
    if _HOOK_DEBUG:
        _HOOK_DEBUG.parent.mkdir(parents=True, exist_ok=True)
        with _HOOK_DEBUG.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def _patch_run_gui_closures() -> bool:
    """在 run_gui 栈帧内批量替换为还原 .py 逻辑（见 charart_hooks.HOOK_SPECS）。"""
    global REFRESH_ART_HOOK_APPLIED
    from charart_hooks import patch_run_gui_closures as _patch

    _debug_hook("_patch_run_gui called")
    ok = _patch(_replace_closure_var, _patch_widget_commands, _debug_hook)
    if ok:
        REFRESH_ART_HOOK_APPLIED = True
    return ok


# 兼容旧名
_patch_refresh_art_in_run_gui_stack = _patch_run_gui_closures


def _install_mainloop_hook() -> None:
    """Patch tk.Misc.mainloop：进入事件循环前替换 run_gui 闭包内的 refresh_art。

    mainloop 定义在 Misc 上（Tk / TkinterDnD.Tk 均继承），须改类方法而非实例属性。
    """
    import tkinter as tk

    if getattr(tk.Misc, "_charart_mainloop_hook_installed", False):
        return

    _orig_mainloop = tk.Misc.mainloop

    def _hooked_mainloop(self, *args, **kwargs):
        _debug_hook(f"mainloop enter ({type(self).__name__})")
        _patch_run_gui_closures()
        return _orig_mainloop(self, *args, **kwargs)

    tk.Misc.mainloop = _hooked_mainloop  # type: ignore[method-assign]
    tk.Misc._charart_mainloop_hook_installed = True  # type: ignore[attr-defined]


def _load_original_module():
    import importlib.util

    pyc = ROOT_DIR / "charart.pyc"
    if not pyc.is_file():
        raise FileNotFoundError(f"缺少 {pyc}")
    spec = importlib.util.spec_from_file_location("charart", pyc)
    if spec is None or spec.loader is None:
        raise ImportError("无法加载 charart.pyc")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["charart"] = mod
    spec.loader.exec_module(mod)
    return mod


def _patch_core(mod) -> None:
    """将已通过 parity 的还原函数注入原版模块。"""
    import charart_core as core

    mod.generate_charart = core.generate_charart
    mod.get_animated_frames = core.get_animated_frames
    mod._charart_from_pil = core._charart_from_pil
    mod._apply_effect = core._apply_effect
    mod._escape_c_string = core._escape_c_string
    mod.art_to_code = core.art_to_code
    mod._render_art_to_image = core._render_art_to_image
    mod._rgba_frames_to_gif_p = core._rgba_frames_to_gif_p
    mod.CHAR_STYLES = core.CHAR_STYLES
    mod.CODE_STYLES = core.CODE_STYLES
    mod.EFFECTS = core.EFFECTS


def run_gui(*, strict: bool = False) -> None:
    """
    启动 GUI。
    strict=True：加载 charart.pyc 原版（验收基准）。
    默认：charart_run_gui.run_gui_native() 纯 Python 实现。
    """
    if strict:
        _install_mainloop_hook()
        mod = _load_original_module()
        _patch_core(mod)
        mod.run_gui()
        return

    from charart_run_gui import run_gui_native

    run_gui_native()


def main() -> None:
    run_gui()


if __name__ == "__main__":
    main()
