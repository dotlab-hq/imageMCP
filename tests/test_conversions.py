"""Tests for image format conversion tools."""

import os
import pytest
from PIL import Image

from imagemcp.tools.conversions import (
    png_to_jpg,
    jpg_to_png,
    webp_to_png,
    svg_to_png,
    png_to_svg,
    image_to_pdf,
    pdf_to_images,
)


def _exists(path):
    assert os.path.exists(path), f"Output file missing: {path}"


def _is_image(path):
    _exists(path)
    img = Image.open(path)
    assert img.size[0] > 0 and img.size[1] > 0
    return img


class TestPngToJpg:
    def test_basic_conversion(self, img_path):
        out = png_to_jpg(img_path)
        _exists(out)
        assert out.endswith(".jpg")

    def test_with_custom_bg(self, img_path):
        out = png_to_jpg(img_path, background_color="#ff0000")
        _exists(out)


class TestJpgToPng:
    def test_basic_conversion(self, img_path):
        out = jpg_to_png(img_path)
        img = _is_image(out)
        assert out.endswith(".png")

    def test_preserves_dimensions(self, img_path):
        orig = Image.open(img_path)
        out = jpg_to_png(img_path)
        img = Image.open(out)
        assert img.size == orig.size


class TestWebpToPng:
    def test_basic_conversion(self, webp_path):
        out = webp_to_png(webp_path)
        img = _is_image(out)
        assert out.endswith(".png")


def _has_cairo():
    try:
        import cairosvg
        cairosvg.svg2png(b'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>')
        return True
    except (OSError, Exception):
        return False


cairo_skip = pytest.mark.skipif(not _has_cairo(), reason="cairosvg requires native Cairo library")


@cairo_skip
class TestSvgToPng:
    def test_basic_conversion(self, svg_path):
        out = svg_to_png(svg_path)
        img = _is_image(out)
        assert out.endswith(".png")

    def test_with_dimensions(self, svg_path):
        out = svg_to_png(svg_path, width=200, height=200)
        img = _is_image(out)
        assert img.size == (200, 200)

    def test_width_only(self, svg_path):
        out = svg_to_png(svg_path, width=100)
        img = _is_image(out)
        assert img.size[0] == 100


class TestPngToSvg:
    def test_basic_conversion(self, img_path):
        out = png_to_svg(img_path)
        _exists(out)
        assert out.endswith(".svg")
        content = open(out).read()
        assert "<svg" in content
        assert "data:image/png;base64" in content


class TestImageToPdf:
    def test_single_image(self, img_path):
        out = image_to_pdf([img_path])
        _exists(out)
        assert out.endswith(".pdf")

    def test_multiple_images(self, img_path, landscape_path):
        out = image_to_pdf([img_path, landscape_path])
        _exists(out)

    def test_three_images(self, assets):
        out = image_to_pdf([assets["dog.jpg"], assets["landscape.jpg"], assets["portrait.jpg"]])
        _exists(out)


class TestPdfToImages:
    def test_basic(self, pdf_path):
        out = pdf_to_images(pdf_path, dpi=72)
        assert isinstance(out, list)
        assert len(out) == 2  # test.pdf has 2 pages
        for p in out:
            img = _is_image(p)

    def test_high_dpi(self, pdf_path):
        out = pdf_to_images(pdf_path, dpi=150)
        assert len(out) == 2
        img = Image.open(out[0])
        assert img.width > 500  # higher DPI = bigger output
