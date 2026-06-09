"""Download test assets into tests/assets/.

Run once before the test suite:
    python -m tests.download_assets

Falls back to Pillow-generated placeholders if downloads fail.
"""

import os
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

DOWNLOADS = {
    "dog.jpg": "https://picsum.photos/id/237/800/600",
    "landscape.jpg": "https://picsum.photos/id/180/800/600",
    "portrait.jpg": "https://picsum.photos/id/65/800/600",
    "ui_screenshot.png": "https://picsum.photos/id/119/1280/720",
    "test.webp": "https://picsum.photos/id/96/400/300",
}


def _generate_placeholder(name: str) -> None:
    """Generate a recognizable Pillow image as a fallback."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 800, 600
    img = Image.new("RGB", (W, H), "#2d3436")
    draw = ImageDraw.Draw(img)

    # Colored rectangles for easier computer-vision testing
    draw.rectangle([0, 0, 400, 300], fill="#0984e3")   # blue top-left
    draw.rectangle([400, 0, 800, 300], fill="#e17055")  # red top-right
    draw.rectangle([0, 300, 400, 600], fill="#00b894")  # green bottom-left
    draw.rectangle([400, 300, 800, 600], fill="#fdcb6e") # yellow bottom-right

    # Central text
    draw.text((W // 2 - 80, H // 2 - 15), "TEST IMAGE", fill="white")

    out = ASSETS_DIR / name
    if out.suffix == ".webp":
        img.save(out, "WEBP")
    elif out.suffix == ".jpg":
        img.save(out, "JPEG")
    else:
        img.save(out, "PNG")


def _generate_ui_placeholder() -> None:
    """Generate a minimal mock UI screenshot."""
    from PIL import Image, ImageDraw

    W, H = 1280, 720
    img = Image.new("RGB", (W, H), "#ffffff")
    draw = ImageDraw.Draw(img)

    # Nav bar
    draw.rectangle([0, 0, W, 60], fill="#1a1a2e")
    draw.rectangle([20, 15, 120, 45], fill="#e94560")   # logo
    draw.text((140, 18), "Nav Item 1", fill="white")
    draw.text((300, 18), "Nav Item 2", fill="white")
    draw.text((460, 18), "Nav Item 3", fill="white")

    # Hero section
    draw.rectangle([0, 60, W, 360], fill="#f0f0f0")
    draw.text((W // 2 - 100, 160), "Welcome Title", fill="#333333")
    draw.text((W // 2 - 60, 200), "Subtitle text", fill="#666666")

    # Button
    draw.rounded_rectangle([W // 2 - 60, 260, W // 2 + 60, 300], radius=8, fill="#e94560")
    draw.text((W // 2 - 30, 268), "Get Started", fill="white")

    # Cards
    for i, color in enumerate(["#0984e3", "#00b894", "#6c5ce7"]):
        x = 100 + i * 380
        draw.rounded_rectangle([x, 400, x + 340, 580], radius=10, fill=color)
        draw.text((x + 20, 420), f"Card {i + 1}", fill="white")

    img.save(ASSETS_DIR / "ui_screenshot.png", "PNG")


def _generate_svg_placeholder() -> None:
    """Generate a simple SVG for conversion tests."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#2d3436"/>
  <circle cx="200" cy="200" r="120" fill="#0984e3"/>
  <circle cx="200" cy="200" r="80" fill="#e17055"/>
  <circle cx="200" cy="200" r="40" fill="#fdcb6e"/>
</svg>"""
    (ASSETS_DIR / "test.svg").write_text(svg)


def _generate_pdf_placeholder() -> None:
    """Generate a simple 2-page PDF."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = ASSETS_DIR / "test.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(72, 700, "Page 1 - Hello from ImageMcp tests")
        c.drawString(72, 650, "This is a test PDF with two pages.")
        c.showPage()
        c.drawString(72, 700, "Page 2 - Second page")
        c.showPage()
        c.save()
    except ImportError:
        pass


def main():
    import urllib.request

    for name, url in DOWNLOADS.items():
        out = ASSETS_DIR / name
        if out.exists():
            print(f"  exists  {name}")
            continue
        try:
            print(f"  downl {name} ...", end=" ", flush=True)
            urllib.request.urlretrieve(url, out)
            print("ok")
        except Exception as e:
            print(f"FAIL ({e}) — generating placeholder")
            _generate_placeholder(name)

    # Always regenerate these (they're generated, not downloaded)
    _generate_ui_placeholder()
    _generate_svg_placeholder()
    _generate_pdf_placeholder()

    print(f"\nAssets ready in {ASSETS_DIR}  ({len(list(ASSETS_DIR.iterdir()))} files)")


if __name__ == "__main__":
    main()
