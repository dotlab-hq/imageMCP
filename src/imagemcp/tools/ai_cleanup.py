"""AI cleanup tools — remove objects, erase text, inpaint regions."""

from PIL import Image, ImageFilter
import numpy as np


def remove_object(image_path: str, x: int, y: int, width: int, height: int) -> str:
    """Remove an object by inpainting the region. Uses OpenAI edit API or local fallback."""
    from imagemcp.utils.io import save_image, load_image
    from imagemcp.utils.ai_client import edit_image, get_client

    # Create mask (white = region to inpaint)
    img = load_image(image_path)
    mask = Image.new("L", img.size, 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.rectangle([x, y, x + width, y + height], fill=255)

    import tempfile, os
    mask_path = os.path.join(tempfile.gettempdir(), "tmp_mask.png")
    mask.save(mask_path)

    client = get_client()
    if client:
        try:
            return edit_image(image_path, mask_path, "Remove the object in the white region, fill with surrounding background")
        except Exception:
            pass

    # Local fallback: Gaussian blur blend
    img_rgb = img.convert("RGB")
    blurred = img_rgb.filter(ImageFilter.GaussianBlur(radius=20))
    mask_arr = np.array(mask).astype(float) / 255.0
    mask_3d = np.stack([mask_arr] * 3, axis=-1)
    result = Image.fromarray((np.array(blurred) * mask_3d + np.array(img_rgb) * (1 - mask_3d)).astype(np.uint8))
    return save_image(result)


def erase_text(image_path: str, x: int | None = None, y: int | None = None, width: int | None = None, height: int | None = None) -> str:
    """Erase text from a region or auto-detect text regions via OCR."""
    from imagemcp.utils.io import save_image, load_image

    if x is not None and y is not None and width is not None and height is not None:
        return remove_object(image_path, x, y, width, height)

    # Auto-detect text via OCR
    img = load_image(image_path)
    try:
        import pytesseract
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        for i, text in enumerate(data["text"]):
            if text.strip():
                rx, ry, rw, rh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                img = Image.open(remove_object(
                    _save_tmp(img), rx, ry, rw, rh
                ))
        return save_image(img)
    except ImportError:
        pass

    # Fallback: no OCR available
    raise RuntimeError("pytesseract not installed and no region specified")


def remove_watermark_candidate(image_path: str) -> str:
    """Detect and remove likely watermark regions (semi-transparent overlays)."""
    from imagemcp.utils.io import save_image, load_image
    img = load_image(image_path).convert("RGB")
    arr = np.array(img).astype(float)

    # Heuristic: find regions with low contrast uniform overlay (common watermark pattern)
    # Look for near-uniform brightness in bottom-right corner (typical watermark location)
    h, w = arr.shape[:2]
    region = arr[int(h * 0.85):, int(w * 0.7):]
    mean_val = region.mean(axis=(0, 1))
    std_val = region.std(axis=(0, 1))

    # If region is unusually uniform, it's likely a watermark
    if std_val.mean() < 30:
        rx, ry = int(w * 0.7), int(h * 0.85)
        return remove_object(image_path, rx, ry, w - rx, h - ry)

    # Fallback: remove bottom-right corner
    return remove_object(image_path, int(w * 0.75), int(h * 0.85), int(w * 0.25), int(h * 0.15))


def inpaint_region(image_path: str, mask_path: str, prompt: str = "") -> str:
    """Inpaint a masked region with optional text prompt."""
    from imagemcp.utils.io import save_image
    from imagemcp.utils.ai_client import edit_image, get_client

    client = get_client()
    if client:
        try:
            return edit_image(image_path, mask_path, prompt or "Fill this region naturally")
        except Exception:
            pass

    # Local fallback: blur inpaint
    from imagemcp.utils.io import load_image
    from PIL import ImageFilter
    img = load_image(image_path).convert("RGB")
    mask = Image.open(mask_path).convert("L")
    blurred = img.filter(ImageFilter.GaussianBlur(radius=20))
    mask_arr = np.array(mask).astype(float) / 255.0
    mask_3d = np.stack([mask_arr] * 3, axis=-1)
    result = Image.fromarray((np.array(blurred) * mask_3d + np.array(img) * (1 - mask_3d)).astype(np.uint8))
    return save_image(result)


def _save_tmp(img: Image.Image) -> str:
    import tempfile, os
    p = os.path.join(tempfile.gettempdir(), "tmp_cleanup.png")
    img.save(p)
    return p
