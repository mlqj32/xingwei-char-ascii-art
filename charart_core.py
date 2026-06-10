# -*- coding: utf-8 -*-
"""
从 charart.pyc 反汇编还原的核心算法（Python 3.13 字节码对照）。
原文件 charart.py 约 line 313-418。
"""
from __future__ import annotations

import os

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise SystemExit("需要安装 Pillow: pip install Pillow") from e

# 自模块常量（与 charart.pyc 一致）
_CELL_W = 8
_CELL_H = 14
ALPHA_THRESHOLD = 30

CHAR_STYLES: dict[str, str] = {
    "默认": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "简洁": " .:-=+*#%@",
    "块状": " ░▒▓█",
    "细腻": " .,'\"^~:;+*?[]()|/\\_-#%&@",
    "线条": " ·'`|/\\-_=+*#",
    "斜线": "  '/\\_|─│┌┐└┘",
    "符号雨": "  0123456789@#$%&*",
    "复古": "  .':;+*?[]()#",
    "极简": "  ░█",
    "高对比": "  ·*#█",
    "格子": "  ─│┼├┤┬┴┌┐└┘",
    "迷宫": "  ··│─┐┘┌└│─",
    "二进制": "  01",
    "字母": "  .aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ",
    "十六进制": " 0123456789ABCDEF",
    "灰度级": " 0123456789",
    "索引色": " 0123456789ABCDEF",
    "位图": " ·█",
    "RGB 通道": " RGBrgb ",
    "像素字节": " 0123456789",
    "4 位深度": " .'`^\",:;Il!i>#%",
    "8 位灰度": " .:-=+*#%@",
    "抖动": "  ░▒▓█",
    "C语言": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Java": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "C++": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Python": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "C#": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "汇编语言": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
}

CODE_STYLES = ["C语言", "Java", "C++", "Python", "C#", "汇编语言"]

EFFECTS = {"正常": 0, "反相": 1, "高对比": 2}


def _escape_c_string(s: str) -> str:
    """line 76-78"""
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def art_to_code(padded_lines: list[str], style_name: str) -> str:
    """line 81-145：字符画转代码风格文本"""
    if not padded_lines:
        return ""
    text = "\n".join(padded_lines)
    if style_name == "C语言":
        lines = ["#include <stdio.h>", "int main(void) {"]
        for line in padded_lines:
            lines.append('    printf("%s\\n");' % _escape_c_string(line))
        lines.extend(["    return 0;", "}"])
        return "\n".join(lines)
    if style_name == "Java":
        lines = ["public class Main {", "    public static void main(String[] args) {"]
        for line in padded_lines:
            lines.append('        System.out.println("%s");' % _escape_c_string(line))
        lines.extend(["    }", "}"])
        return "\n".join(lines)
    if style_name == "C++":
        lines = ["#include <iostream>", "int main() {"]
        for line in padded_lines:
            lines.append('    std::cout << "%s" << std::endl;' % _escape_c_string(line))
        lines.extend(["    return 0;", "}"])
        return "\n".join(lines)
    if style_name == "Python":
        escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
        return f'art = """{escaped}"""\nprint(art)'
    if style_name == "C#":
        lines = ["using System;", "class Program {", "    static void Main() {"]
        for line in padded_lines:
            lines.append('        Console.WriteLine("%s");' % _escape_c_string(line))
        lines.extend(["    }", "}"])
        return "\n".join(lines)
    if style_name == "汇编语言":
        parts = ['"%s"' % _escape_c_string(line) for line in padded_lines]
        db_line = "    msg: db " + ", 10, ".join(parts) + ", 10"
        lines = [
            "section .data",
            db_line,
            "    len: equ $ - msg",
            "section .text",
            "    global _start",
            "_start:",
            "    mov rax, 1",
            "    mov rdi, 1",
            "    mov rsi, msg",
            "    mov rdx, len",
            "    syscall",
            "    mov rax, 60",
            "    xor rdi, rdi",
            "    syscall",
        ]
        return "\n".join(lines)
    return text


def _apply_effect(lum: int, effect: int) -> int:
    """line 313-325"""
    if effect == 0:
        return lum
    if effect == 1:
        return 255 - lum
    if effect == 2:
        if lum < 85:
            return 0
        if lum > 170:
            return 255
        return 128
    return lum


def _charart_from_pil(
    img: Image.Image,
    max_width: int,
    max_height: int | None,
    chars: str,
    effect: int = 0,
    return_colors: bool = False,
    transparent_bg: tuple[int, int, int] = (128, 128, 128),
):
    """line 328-366：PIL 图 → 字符行列表"""
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    w, h = img.size
    if max_height is None:
        max_height = max_width

    scale_h = min(max_height / h, max_width / w * (_CELL_W / _CELL_H))
    scale_w = scale_h * (_CELL_H / _CELL_W)
    new_w = max(1, min(max_width, int(w * scale_w)))
    new_h = max(1, min(max_height, int(h * scale_h)))
    img = img.resize((new_w, new_h), Image.Resampling.NEAREST)

    nch = len(chars)
    out: list[str] = []
    colors = [] if return_colors else None
    tr, tg, tb = transparent_bg

    for y in range(new_h):
        line: list[str] = []
        row_colors = [] if return_colors else None
        for x in range(new_w):
            r, g, b, a = img.getpixel((x, y))
            if a < ALPHA_THRESHOLD:
                r, g, b = tr, tg, tb
            lum = int(0.299 * r + 0.587 * g + 0.114 * b)
            lum = _apply_effect(lum, effect)
            idx = min(lum * nch // 256, nch - 1)
            line.append(chars[idx])
            if return_colors and row_colors is not None:
                row_colors.append((r, g, b))
        out.append("".join(line))
        if return_colors and colors is not None and row_colors is not None:
            colors.append(row_colors)

    if return_colors:
        return out, colors, new_w, new_h
    return out, new_w, new_h


def generate_charart(
    image_path: str,
    max_width: int = 80,
    max_height: int | None = None,
    chars: str | None = None,
    effect: int = 0,
    transparent_bg: tuple[int, int, int] = (128, 128, 128),
):
    """line 369-381：从文件路径生成字符画"""
    if not image_path or not os.path.isfile(image_path):
        return None, 0, 0
    if chars is None:
        chars = CHAR_STYLES["默认"]
    try:
        img = Image.open(image_path).convert("RGBA")
    except Exception:
        return None, 0, 0
    return _charart_from_pil(
        img,
        max_width,
        max_height,
        chars,
        effect,
        transparent_bg=transparent_bg,
    )


def get_animated_frames(image_path: str, max_frames: int = 400):
    """line 385-418：GIF 等动图拆帧"""
    if not image_path or not os.path.isfile(image_path):
        return [], []
    try:
        img = Image.open(image_path)
    except Exception:
        return [], []

    n = getattr(img, "n_frames", 1)
    if n <= 1:
        img.seek(0)
        frames = [img.copy().convert("RGBA")]
        dur = img.info.get("duration", 100)
        if isinstance(dur, (list, tuple)) and dur:
            dur = dur[0]
        return frames, [max(20, int(dur))]

    step = max(1, n // max_frames)
    frames: list[Image.Image] = []
    durations: list[int] = []
    for i in range(0, n, step):
        if len(frames) >= max_frames:
            break
        img.seek(i)
        frames.append(img.copy().convert("RGBA"))
        dur = img.info.get("duration", 100)
        if isinstance(dur, (list, tuple)) and i < len(dur):
            dur = dur[i]
        durations.append(max(20, int(dur)))

    if not frames:
        return [], []
    return frames, durations


def _rgba_frames_to_gif_p(frames_rgba: list, durations_ms: list):
    """line 235-276：RGBA 帧序列 → 调色板 GIF 帧"""
    if not frames_rgba:
        return [], []

    unique_rgb: set[tuple[int, int, int]] = set()
    for img in frames_rgba:
        if img.mode != "RGBA":
            continue
        for p in img.getdata():
            if len(p) >= 4 and p[3] >= 128:
                unique_rgb.add((p[0], p[1], p[2]))

    unique_rgb = list(unique_rgb)[:255]
    if not unique_rgb:
        unique_rgb = [(255, 255, 255)]

    palette: list[int] = [0, 0, 0]
    for r, g, b in unique_rgb:
        palette.extend([r, g, b])
    while len(palette) < 768:
        palette.extend([0, 0, 0])

    rgb_to_idx = {t: i + 1 for i, t in enumerate(unique_rgb)}
    out_frames: list[Image.Image] = []

    for img in frames_rgba:
        if img.mode != "RGBA":
            out_frames.append(img.convert("P"))
            continue
        w, h = img.size
        out = Image.new("P", (w, h))
        out.putpalette(palette[:768])
        data = img.getdata()
        for y in range(h):
            for x in range(w):
                p = data[y * w + x]
                if len(p) >= 4 and p[3] < 128:
                    out.putpixel((x, y), 0)
                else:
                    rgb = (p[0], p[1], p[2])
                    out.putpixel((x, y), rgb_to_idx.get(rgb, 1))
        out.info["transparency"] = 0
        out_frames.append(out)

    return out_frames, durations_ms


def _render_art_to_image(
    padded: list[str],
    padded_colors: list | None = None,
    bg_rgb: tuple[int, int, int] | None = None,
):
    """line 279-310：字符画渲染为 PIL 图像"""
    if not padded:
        if bg_rgb is None:
            return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return Image.new("RGB", (1, 1), bg_rgb)

    rows = len(padded)
    cols = len(padded[0]) if padded[0] else 0
    w, h = cols * _CELL_W, rows * _CELL_H

    if bg_rgb is None:
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    else:
        img = Image.new("RGB", (w, h), bg_rgb)

    draw = ImageDraw.Draw(img)
    font = None
    for path in (
        "C:/Windows/Fonts/consola.ttf",
        "consola.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ):
        try:
            font = ImageFont.truetype(path, 12)
            break
        except (OSError, IOError):
            continue
    if font is None:
        font = ImageFont.load_default()

    if bg_rgb is None or sum(bg_rgb) < 384:
        fg: tuple[int, ...] = (255, 255, 255)
    else:
        fg = (0, 0, 0)

    for r, line in enumerate(padded):
        for c, ch in enumerate(line):
            if c >= cols:
                break
            color = fg
            if (
                padded_colors
                and r < len(padded_colors)
                and c < len(padded_colors[r])
            ):
                color = tuple(padded_colors[r][c][:3])
            draw.text((c * _CELL_W, r * _CELL_H), ch, fill=color, font=font)

    return img
