"""Design analysis tools — extract colors, typography, layout, components."""

from PIL import Image
import numpy as np


def extract_colors(image_path: str, count: int = 5) -> list[dict]:
    """Extract dominant colors. Local Pillow quantize with AI fallback."""
    from imagemcp.utils.io import load_image
    from imagemcp.utils.ai_client import vision_json

    img = load_image(image_path).convert("RGB")
    # Resize for speed
    small = img.resize((150, 150), Image.LANCZOS)
    quantized = small.quantize(colors=count, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()

    total_pixels = 150 * 150
    color_counts = quantized.getcolors()
    results = []
    for count_val, idx in sorted(color_counts, reverse=True):
        r, g, b = palette[idx * 3], palette[idx * 3 + 1], palette[idx * 3 + 2]
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        pct = round(count_val / total_pixels * 100, 1)
        results.append({"hex": hex_color, "rgb": [r, g, b], "pct": pct})
    return results[:count]


def extract_typography(image_path: str) -> list[dict]:
    """Extract typography info using GPT-4o vision."""
    from imagemcp.utils.ai_client import vision_json
    prompt = (
        "Identify all visible text in this image. For each unique text element, "
        "return JSON: [{\"text\": str, \"font_family\": str, \"font_size_estimate\": str, "
        "\"weight\": str, \"color\": str}]"
    )
    return vision_json(image_path, prompt)


def detect_layout(image_path: str) -> dict:
    """Detect layout structure using GPT-4o vision."""
    from imagemcp.utils.ai_client import vision_json
    prompt = (
        "Analyze the layout of this UI image. Return JSON: "
        '{"sections": [{"name": str, "bounds": {"x": int, "y": int, "w": int, "h": int}, '
        '"type": str}], "alignment": str, "grid": str, "spacing_estimate": str}'
    )
    return vision_json(image_path, prompt)


def describe_design(image_path: str) -> str:
    """Get a natural language design description."""
    from imagemcp.utils.ai_client import vision_describe
    return vision_describe(
        image_path,
        "Describe this design in detail: style, color scheme, layout, typography, "
        "mood, and any notable design patterns or UI components."
    )


def identify_components(image_path: str) -> list[dict]:
    """Identify UI components with bounding boxes."""
    from imagemcp.utils.ai_client import vision_json
    prompt = (
        "Identify all UI components in this image. Return JSON: "
        '[{"component": str, "bounds": {"x": int, "y": int, "w": int, "h": int}, '
        '"confidence": str}]'
    )
    return vision_json(image_path, prompt)
