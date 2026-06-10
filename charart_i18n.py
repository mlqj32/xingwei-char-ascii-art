# -*- coding: utf-8 -*-
"""多语言文案与模块常量。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from charart_core import CHAR_STYLES, CODE_STYLES, EFFECTS


def _resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent


ROOT_DIR = _resource_root()
I18N_PATH = ROOT_DIR / "docs" / "module_constants.json"

SUPPORTED_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tiff", ".tif", ".ico",
)

ALPHA_THRESHOLD = 30
LARGE_SIZE_THRESHOLD = 10000
RECENT_MAX = 10

# 字符生成用背景色（line 588）；与 UI 下拉 TRANSPARENT_OPTIONS 不同
GEN_TRANSPARENT_BG: dict[str, tuple[int, int, int]] = {
    "透明": (0, 0, 0),
    "黑": (40, 40, 40),
    "白": (255, 255, 255),
    "灰": (128, 128, 128),
}

TRANSPARENT_VAR_OPTIONS: tuple[str, ...] = ("透明", "黑", "白", "灰")
TRANSPARENT_OPTION_I18N: dict[str, str] = {
    "透明": "opt_transparent",
    "黑": "opt_black",
    "白": "opt_white",
    "灰": "opt_gray",
}

EXPORT_BG_VAR_OPTIONS: tuple[str, ...] = ("透明", "黑", "白", "预览区")
EXPORT_BG_OPTION_I18N: dict[str, str] = {
    "透明": "opt_transparent",
    "黑": "opt_black",
    "白": "opt_white",
    "预览区": "opt_preview_bg",
}

EXPORT_BG_OPTIONS: dict[str, tuple[int, int, int] | None] = {
    "透明": None,
    "黑": (0, 0, 0),
    "白": (255, 255, 255),
    "预览区": (40, 22, 38),
}

DEFAULT_PAD_COLOR = (40, 40, 40)


def _load_i18n() -> dict:
    if I18N_PATH.is_file():
        data = json.loads(I18N_PATH.read_text(encoding="utf-8"))
        i18n = data.get("I18N", {})
        if isinstance(i18n, dict):
            return i18n
    return {}


I18N: dict = _load_i18n()


def _t(lang: str, key: str) -> str:
    """line 225-228"""
    d = I18N.get(key, {})
    if isinstance(d, dict):
        return d.get(lang, d.get("zh", key))
    return key
