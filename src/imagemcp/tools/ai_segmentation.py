"""AI segmentation and selection tools — background removal, object extraction, masking."""

import io
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from pathlib import Path
from PIL import Image
import numpy as np

import logging

logger = logging.getLogger(__name__)

_BG_REMOVE_TIMEOUT = int(os.environ.get("IMAGEMCP_BG_TIMEOUT", "60"))


def _check_onnxruntime():
    """Verify CPU-only onnxruntime is installed. Warn loudly if GPU variant is present."""
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers:
            logger.warning(
                "onnxruntime-gpu detected (CUDAExecutionProvider available). "
                "This CAN hang on systems without proper CUDA/cuDNN. "
                "Run: pip uninstall onnxruntime-gpu && pip install onnxruntime"
            )
        else:
            logger.info("onnxruntime providers: %s", providers)
    except Exception as e:
        logger.warning("Could not check onnxruntime: %s", e)


def _rembg_remove(image_path: str) -> Image.Image:
    from rembg import new_session, remove

    def _do_remove() -> bytes:
        _check_onnxruntime()
        session = new_session("u2net", providers=["CPUExecutionProvider"])
        with open(image_path, "rb") as f:
            input_data = f.read()
        logger.info("rembg: session ready, starting remove on %s (%d bytes)", image_path, len(input_data))
        return remove(input_data, session=session)

    logger.info("rembg: starting background removal (timeout=%ds) for %s", _BG_REMOVE_TIMEOUT, image_path)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_do_remove)
        try:
            output_data = future.result(timeout=_BG_REMOVE_TIMEOUT)
        except FuturesTimeout:
            future.cancel()
            raise RuntimeError(
                f"Background removal timed out after {_BG_REMOVE_TIMEOUT}s. "
                "onnxruntime-gpu is likely installed — it hangs when CUDA libs are missing. "
                "Fix: pip uninstall onnxruntime-gpu && pip install onnxruntime"
            )
    return Image.open(io.BytesIO(output_data)).convert("RGBA")


def extract_subject(image_path: str) -> str:
    """Extract the main subject from an image by removing the background."""
    from imagemcp.utils.io import save_image
    img = _rembg_remove(image_path)
    return save_image(img)


def extract_person(image_path: str) -> str:
    """Extract person — rembg is tuned for people, same as extract_subject."""
    return extract_subject(image_path)


def extract_face(image_path: str) -> list[str]:
    """Extract faces using Haar cascade from OpenCV or PIL-based detection."""
    from imagemcp.utils.io import save_image
    img = Image.open(image_path).convert("RGB")

    # Try OpenCV first
    try:
        import cv2
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, 1.1, 4)
        paths = []
        for (x, y, w, h) in faces:
            face_crop = img.crop((x, y, x + w, y + h))
            paths.append(save_image(face_crop))
        if paths:
            return paths
    except ImportError:
        pass

    # Fallback: return the whole image
    return [save_image(img)]


def extract_object(image_path: str, description: str) -> str:
    """Extract a described object using GPT-4o vision for bbox + rembg for isolation."""
    from imagemcp.utils.io import save_image, load_image
    from imagemcp.utils.ai_client import vision_json

    prompt = (
        f'Find the bounding box of the object described as "{description}" in this image. '
        "Return JSON: {\"x\": int, \"y\": int, \"width\": int, \"height\": int}"
    )
    bbox = vision_json(image_path, prompt)
    img = load_image(image_path)
    x, y, w, h = bbox["x"], bbox["y"], bbox["width"], bbox["height"]
    crop = img.crop((x, y, x + w, y + h))

    # Save temp, remove bg
    import tempfile, os
    tmp = os.path.join(tempfile.gettempdir(), "tmp_crop.png")
    crop.save(tmp)
    result = _rembg_remove(tmp)
    return save_image(result)


def remove_background(image_path: str) -> str:
    """Remove the background from an image, leaving only the foreground subject."""
    from imagemcp.utils.io import save_image
    img = _rembg_remove(image_path)
    return save_image(img)


def generate_mask(image_path: str, description: str) -> str:
    """Generate a binary mask for the described region."""
    from imagemcp.utils.io import save_image, load_image
    from imagemcp.utils.ai_client import vision_json

    prompt = (
        f'Find the region matching "{description}". '
        "Return JSON with polygon points: {\"points\": [[x,y], ...]}"
    )
    result = vision_json(image_path, prompt)
    img = load_image(image_path)
    mask = Image.new("L", img.size, 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    points = [(p[0], p[1]) for p in result["points"]]
    draw.polygon(points, fill=255)
    return save_image(mask)
