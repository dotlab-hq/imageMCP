"""Image I/O helpers — load, save, temp paths."""

import os
import tempfile
from pathlib import Path
from PIL import Image

STORAGE = Path(os.environ.get("IMAGEMCP_STORAGE", tempfile.gettempdir())) / "imagemcp"
STORAGE.mkdir(parents=True, exist_ok=True)

_counter = 0


def _next_path(extension: str = "png") -> Path:
    global _counter
    _counter += 1
    return STORAGE / f"{_counter:06d}.{extension}"


def load_image(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save_image(img: Image.Image, ext: str = "png") -> str:
    out = _next_path(ext)
    if ext == "jpg":
        img = img.convert("RGB")
    img.save(out, quality=95)
    return str(out)


def temp_path(ext: str = "png") -> str:
    return str(_next_path(ext))
