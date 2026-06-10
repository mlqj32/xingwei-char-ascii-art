# -*- coding: utf-8 -*-
"""核心算法与导出链路自检。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import charart_core as core


def _check(name: str, ok: bool) -> bool:
    print(f"  {'OK' if ok else 'FAIL'} {name}")
    return ok


def main() -> int:
    ok_all = True
    print("=== 模块级常量 ===")
    ok_all &= _check("_apply_effect(128,0)", core._apply_effect(128, 0) == 128)
    ok_all &= _check("_apply_effect(128,1)", core._apply_effect(128, 1) == 127)
    ok_all &= _check("_apply_effect(50,2)", core._apply_effect(50, 2) == 0)
    ok_all &= _check(
        "_escape_c_string",
        core._escape_c_string('a"b\n\t\\') == 'a\\"b\\n\\t\\\\',
    )
    ok_all &= _check(
        "art_to_code(C语言)",
        "printf" in core.art_to_code(["@@"], "C语言"),
    )
    ok_all &= _check(
        "art_to_code(Python)",
        '"""' in core.art_to_code(["hi"], "Python"),
    )
    ok_all &= _check(
        "art_to_code(汇编语言)",
        "section .data" in core.art_to_code(["x"], "汇编语言"),
    )

    icon = ROOT / "icon.png"
    if icon.is_file():
        print("=== 图像算法 (icon.png) ===")
        lines, w, h = core.generate_charart(str(icon), max_width=40)
        ok_all &= _check("generate_charart w=40", bool(lines) and w > 0 and h > 0)
        lines80, _, _ = core.generate_charart(str(icon), max_width=80)
        ok_all &= _check("generate_charart w=80", bool(lines80))
        frames, durs = core.get_animated_frames(str(icon))
        ok_all &= _check("get_animated_frames", len(frames) >= 1)
        if lines:
            img = core._render_art_to_image(lines, None, (255, 255, 255))
            ok_all &= _check("_render_art_to_image", img.size[0] > 0)
        if frames:
            gif_p, gif_d = core._rgba_frames_to_gif_p(frames[:1], durs[:1] or [100])
            ok_all &= _check(
                f"_rgba_frames_to_gif_p (count={len(gif_p)})",
                len(gif_p) >= 1 and len(gif_d) >= 1,
            )
    else:
        print("  (跳过 icon.png 图像测试)")

    if ok_all:
        print("\n全部通过")
        return 0
    print("\n存在失败项")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
