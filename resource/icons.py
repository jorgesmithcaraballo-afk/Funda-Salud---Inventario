"""
Icon utilities: load and cache CTkImage icons from resource/img
"""
from __future__ import annotations

from functools import lru_cache
from typing import Tuple
from PIL import Image
import customtkinter as ctk
import os

# Base path for icons
ICON_DIR = os.path.join(os.path.dirname(__file__), "img")

# Map logical names to filenames
ICON_MAP = {
    "arrow_back": "arrow_back.png",
    "chat": "chat.png",
    "settings": "settings.png",
    "check_circle": "check_circle.png",
    "home": "home.png",
    "report": "report.png",
    "update": "update.png",
    "logo": "logo.png",
}


def _icon_path(name: str) -> str:
    filename = ICON_MAP.get(name)
    if not filename:
        raise ValueError(f"Icon '{name}' not found in ICON_MAP")
    path = os.path.join(ICON_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Icon file not found: {path}")
    return path


@lru_cache(maxsize=64)
def get_icon(name: str, size: Tuple[int, int] = (28, 28)) -> ctk.CTkImage:
    """Return a cached CTkImage for the given icon name and size.

    Parameters:
        name: Logical icon name (see ICON_MAP)
        size: (width, height) in pixels
    """
    path = _icon_path(name)
    img = Image.open(path)
    return ctk.CTkImage(light_image=img, size=size)
