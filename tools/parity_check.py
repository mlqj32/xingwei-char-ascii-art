# -*- coding: utf-8 -*-
"""对照 charart.pyc 与还原模块，验证行为是否一致。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _load_pyc():
    spec = importlib.util.spec_from_file_location("charart_pyc", ROOT / "charart.pyc")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _compare(name: str, pyc_fn, py_fn, *args, **kwargs) -> bool:
    pyc_out = pyc_fn(*args, **kwargs)
    py_out = py_fn(*args, **kwargs)
    ok = pyc_out == py_out
    print(f"  {'OK' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"    pyc: {repr(pyc_out)[:120]}")
        print(f"    py : {repr(py_out)[:120]}")
    return ok


def _compare_images(name: str, img_a, img_b) -> bool:
    ok = img_a.size == img_b.size and img_a.mode == img_b.mode and img_a.tobytes() == img_b.tobytes()
    print(f"  {'OK' if ok else 'FAIL'} {name}")
    if not ok:
        print(f"    size/mode pyc={img_a.size}/{img_a.mode} py={img_b.size}/{img_b.mode}")
    return ok


def main() -> int:
    import charart_core as core

    pyc = _load_pyc()
    icon = ROOT / "icon.png"
    ok_all = True

    print("=== 模块级函数 ===")
    ok_all &= _compare("_apply_effect(128,0)", pyc._apply_effect, core._apply_effect, 128, 0)
    ok_all &= _compare("_apply_effect(128,1)", pyc._apply_effect, core._apply_effect, 128, 1)
    ok_all &= _compare("_apply_effect(50,2)", pyc._apply_effect, core._apply_effect, 50, 2)
    ok_all &= _compare("_escape_c_string", pyc._escape_c_string, core._escape_c_string, 'a"b\n\t\\')

    sample_lines = ["abc", "de"]
    for style in ("C语言", "Python", "汇编语言", "默认"):
        if style == "默认":
            py_style = "未知"
            continue
        ok_all &= _compare(
            f"art_to_code({style})",
            pyc.art_to_code,
            core.art_to_code,
            sample_lines,
            style,
        )

    if icon.is_file():
        print("=== 图像算法 (icon.png) ===")
        for w in (40, 80):
            ok_all &= _compare(
                f"generate_charart w={w}",
                pyc.generate_charart,
                core.generate_charart,
                str(icon),
                w,
            )

        ok_all &= _compare(
            "get_animated_frames",
            lambda p: (len(pyc.get_animated_frames(p)[0]), pyc.get_animated_frames(p)[1]),
            lambda p: (len(core.get_animated_frames(p)[0]), core.get_animated_frames(p)[1]),
            str(icon),
        )

        lines, _, _ = pyc.generate_charart(str(icon), max_width=40)
        if lines:
            ok_all &= _compare_images(
                "_render_art_to_image",
                pyc._render_art_to_image(lines, None, (255, 255, 255)),
                core._render_art_to_image(lines, None, (255, 255, 255)),
            )

        frames, durs = pyc.get_animated_frames(str(icon))
        if frames:
            pyc_p, pyc_d = pyc._rgba_frames_to_gif_p(frames[:1], durs[:1])
            py_p, py_d = core._rgba_frames_to_gif_p(frames[:1], durs[:1])
            ok_all &= len(pyc_p) == len(py_p) and pyc_d == py_d
            print(f"  {'OK' if ok_all else 'FAIL'} _rgba_frames_to_gif_p (count={len(pyc_p)})")

    print()
    if ok_all:
        print("全部通过 — 已还原函数与 pyc 行为一致")
        return 0
    print("存在差异 — 请修正还原模块后再注入 pyc")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
