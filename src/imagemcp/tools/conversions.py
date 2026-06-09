"""Image format conversions."""

import io
from pathlib import Path
from PIL import Image


def png_to_jpg(image_path: str, background_color: str = "#ffffff") -> str:
    """Convert a PNG image to JPG, compositing transparency over the given background color."""
    from imagemcp.utils.io import save_image
    img = Image.open(image_path).convert("RGBA")
    bg = Image.new("RGBA", img.size, background_color)
    bg.paste(img, mask=img.split()[3])
    return save_image(bg.convert("RGB"), ext="jpg")


def jpg_to_png(image_path: str) -> str:
    """Convert a JPG image to PNG format."""
    from imagemcp.utils.io import save_image
    img = Image.open(image_path).convert("RGB")
    return save_image(img, ext="png")


def webp_to_png(image_path: str) -> str:
    """Convert a WebP image to PNG format."""
    from imagemcp.utils.io import save_image
    img = Image.open(image_path).convert("RGBA")
    return save_image(img, ext="png")


def svg_to_png(image_path: str, width: int | None = None, height: int | None = None) -> str:
    """Convert an SVG file to PNG, optionally specifying output dimensions."""
    import cairosvg
    from imagemcp.utils.io import _next_path
    out = _next_path("png")
    kwargs = {"url": image_path, "write_to": str(out)}
    if width:
        kwargs["output_width"] = width
    if height:
        kwargs["output_height"] = height
    cairosvg.svg2png(**kwargs)
    return str(out)


def png_to_svg(image_path: str) -> str:
    """Convert a PNG image to SVG by embedding it as a base64 data URI."""
    from imagemcp.utils.io import _next_path
    img = Image.open(image_path).convert("RGBA")
    w, h = img.size
    # Embed as base64 PNG inside SVG
    import base64
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">
  <image href="data:image/png;base64,{img_b64}" width="{w}" height="{h}"/>
</svg>'''
    out = _next_path("svg")
    out.write_text(svg)
    return str(out)


def image_to_pdf(image_paths: list[str]) -> str:
    """Combine multiple images into a single PDF document."""
    from imagemcp.utils.io import _next_path
    out = _next_path("pdf")
    images = []
    for p in image_paths:
        img = Image.open(p).convert("RGB")
        images.append(img)
    if images:
        images[0].save(str(out), save_all=True, append_images=images[1:])
    return str(out)


def pdf_to_images(pdf_path: str, dpi: int = 150) -> list[str]:
    """Convert each page of a PDF to a separate PNG image at the given DPI."""
    import fitz  # PyMuPDF
    from imagemcp.utils.io import _next_path
    doc = fitz.open(pdf_path)
    paths = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        out = _next_path("png")
        pix.save(str(out))
        paths.append(str(out))
    return paths
