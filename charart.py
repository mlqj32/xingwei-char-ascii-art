# -*- coding: utf-8 -*-
"""
星薇字符画 — 统一入口。

GUI：charart_run_gui.run_gui_native()
CLI：python charart.py --cli
"""
from __future__ import annotations

import os
import sys

from charart_core import (  # noqa: F401
    CHAR_STYLES,
    CODE_STYLES,
    EFFECTS,
    _apply_effect,
    _charart_from_pil,
    _escape_c_string,
    _render_art_to_image,
    _rgba_frames_to_gif_p,
    art_to_code,
    generate_charart,
    get_animated_frames,
)
from charart_display import (  # noqa: F401
    DEFAULT_PAD_COLOR,
    pad_to_display,
    pad_to_display_static,
    stop_animation_logic,
)
from charart_export import (  # noqa: F401
    copy_art_logic,
    export_gif_logic,
    export_html_logic,
    export_png_logic,
    export_txt_logic,
    get_art_html_logic,
    get_art_text_logic,
)
from charart_i18n import (  # noqa: F401
    ALPHA_THRESHOLD,
    EXPORT_BG_OPTIONS,
    GEN_TRANSPARENT_BG,
    I18N,
    LARGE_SIZE_THRESHOLD,
    RECENT_MAX,
    SUPPORTED_EXTENSIONS,
    _t,
)

__doc__ = "从图片解析非透明部分生成等比例字符画（支持 PNG/JPG/BMP/GIF/WebP 等）"


def run_gui(*, strict: bool = False) -> None:
    from charart_gui import run_gui as _run_gui

    _run_gui(strict=strict)


def main() -> None:
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "萝薇日常.png")
    if "--cli" in sys.argv:
        chars = CHAR_STYLES["默认"]
        lines, _, _ = generate_charart(path, max_width=80, chars=chars)
        if not lines:
            print("未找到 萝薇日常.png")
            return
        print("\n========== 星薇字符画 · 星辰幻境工作室 ==========\n")
        print("\n".join(lines))
        print("\n================================================\n")
        return
    run_gui()


if __name__ == "__main__":
    main()
