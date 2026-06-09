"""Smart export tools — export canvas to PNG, SVG, React, Tailwind, Figma JSON."""

from pathlib import Path
from PIL import Image


def export_png(document_id: str | None = None, image_path: str | None = None) -> str:
    """Export as PNG. Accepts a document_id or direct image_path."""
    from imagemcp.utils.io import save_image, load_image
    if document_id:
        from imagemcp.utils.canvas import get_canvas
        canvas = get_canvas(document_id)
        return save_image(canvas.flatten(), ext="png")
    elif image_path:
        img = load_image(image_path)
        return save_image(img, ext="png")
    raise ValueError("Provide document_id or image_path")


def export_svg(document_id: str | None = None, image_path: str | None = None) -> str:
    """Export as SVG with embedded raster image."""
    from imagemcp.utils.io import _next_path, load_image
    import base64, io

    if document_id:
        from imagemcp.utils.canvas import get_canvas
        img = get_canvas(document_id).flatten()
    elif image_path:
        img = load_image(image_path)
    else:
        raise ValueError("Provide document_id or image_path")

    w, h = img.size
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <image href="data:image/png;base64,{b64}" width="{w}" height="{h}"/>
</svg>'''
    out = _next_path("svg")
    out.write_text(svg)
    return str(out)


def export_react(document_id: str | None = None, image_path: str | None = None) -> str:
    """Generate a React component that reconstructs the visual layout."""
    from imagemcp.utils.ai_client import vision_describe
    from imagemcp.utils.io import load_image, save_image

    if document_id:
        from imagemcp.utils.canvas import get_canvas
        img = get_canvas(document_id).flatten()
        tmp_path = save_image(img)
    else:
        tmp_path = image_path

    if not tmp_path:
        raise ValueError("Provide document_id or image_path")

    return vision_describe(
        tmp_path,
        "Convert this image into a React component using TypeScript and Tailwind CSS. "
        "Recreate the visual layout with divs, appropriate spacing, colors, and typography. "
        "Output ONLY the component code."
    )


def export_tailwind(document_id: str | None = None, image_path: str | None = None) -> str:
    """Generate HTML with Tailwind classes."""
    from imagemcp.utils.ai_client import vision_describe
    from imagemcp.utils.io import load_image, save_image

    if document_id:
        from imagemcp.utils.canvas import get_canvas
        img = get_canvas(document_id).flatten()
        tmp_path = save_image(img)
    else:
        tmp_path = image_path

    if not tmp_path:
        raise ValueError("Provide document_id or image_path")

    return vision_describe(
        tmp_path,
        "Convert this image into clean HTML using Tailwind CSS utility classes. "
        "Recreate the visual layout accurately with appropriate spacing, colors, fonts. "
        "Output ONLY the HTML code."
    )


def export_figma_json(document_id: str | None = None, image_path: str | None = None) -> dict:
    """Export layout as Figma-compatible JSON structure."""
    from imagemcp.utils.ai_client import vision_json
    from imagemcp.utils.io import save_image, load_image
    from imagemcp.utils.canvas import get_canvas

    if document_id:
        canvas = get_canvas(document_id)
        layers = canvas.list_layers()
        img = canvas.flatten()
        tmp_path = save_image(img)
    elif image_path:
        img = load_image(image_path)
        tmp_path = image_path
        layers = [{"name": "root", "x": 0, "y": 0, "width": img.width, "height": img.height}]
    else:
        raise ValueError("Provide document_id or image_path")

    structure = vision_json(
        tmp_path,
        "Analyze this design and output a Figma-compatible JSON structure:\n"
        '{"nodes": [{"id": str, "name": str, "type": "FRAME"|"TEXT"|"RECTANGLE"|"GROUP", '
        '"absoluteBoundingBox": {"x": int, "y": int, "width": int, "height": int}, '
        '"fills": [{"color": str}], "children": [...]}]}\n'
        "Recreate the full component tree."
    )

    structure["canvas_layers"] = layers
    return structure
