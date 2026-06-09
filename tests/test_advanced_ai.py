"""Tests for advanced AI features.

Tools with API fallbacks are tested locally first; API paths skipped without key.
"""

import os
import pytest
from PIL import Image
import numpy as np

from imagemcp.utils.ai_client import get_client

HAS_API = get_client() is not None
api_skip = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


def _is_image(path):
    assert os.path.exists(path), f"Missing: {path}"
    img = Image.open(path)
    assert img.size[0] > 0 and img.size[1] > 0
    return img


class TestPhotoToHeadshot:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_headshot
        out = photo_to_headshot(img_path)
        img = _is_image(out)
        # Cropped center, so should be smaller
        assert img.width <= 800
        assert img.height <= 600


class TestPhotoToCartoon:
    def test_local_fallback_default(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_cartoon
        out = photo_to_cartoon(img_path)
        _is_image(out)

    def test_local_fallback_anime(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_cartoon
        out = photo_to_cartoon(img_path, style="anime")
        _is_image(out)

    def test_original_not_modified(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_cartoon
        orig_hash = hash(open(img_path, "rb").read())
        photo_to_cartoon(img_path)
        new_hash = hash(open(img_path, "rb").read())
        assert orig_hash == new_hash


class TestPhotoToVector:
    @api_skip
    def test_returns_svg(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_vector
        out = photo_to_vector(img_path)
        assert out.endswith(".svg")
        content = open(out).read()
        assert "<svg" in content


class TestPhotoTo3d:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_3d
        out = photo_to_3d(img_path)
        _is_image(out)

    def test_output_same_dimensions(self, img_path):
        from imagemcp.tools.advanced_ai import photo_to_3d
        orig = Image.open(img_path)
        out = Image.open(photo_to_3d(img_path))
        assert out.size == orig.size


class TestStyleTransfer:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.advanced_ai import style_transfer
        out = style_transfer(img_path, style_name="sketch")
        _is_image(out)

    def test_pixel_art_style(self, img_path):
        from imagemcp.tools.advanced_ai import style_transfer
        out = style_transfer(img_path, style_name="pixel_art")
        _is_image(out)

    def test_output_same_dimensions(self, img_path):
        from imagemcp.tools.advanced_ai import style_transfer
        orig = Image.open(img_path)
        out = Image.open(style_transfer(img_path, style_name="impressionist"))
        assert out.size == orig.size


class TestFaceEnhancement:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.advanced_ai import face_enhancement
        out = face_enhancement(img_path)
        _is_image(out)

    def test_output_same_dimensions(self, img_path):
        from imagemcp.tools.advanced_ai import face_enhancement
        orig = Image.open(img_path)
        out = Image.open(face_enhancement(img_path))
        assert out.size == orig.size


class TestUpscaleImage:
    def test_2x_upscale(self, img_path):
        from imagemcp.tools.advanced_ai import upscale_image
        out = upscale_image(img_path, scale_factor=2)
        img = _is_image(out)
        assert img.size == (1600, 1200)

    def test_3x_upscale(self, img_path):
        from imagemcp.tools.advanced_ai import upscale_image
        out = upscale_image(img_path, scale_factor=3)
        img = _is_image(out)
        assert img.size == (2400, 1800)

    def test_default_2x(self, img_path):
        from imagemcp.tools.advanced_ai import upscale_image
        out = upscale_image(img_path)
        img = _is_image(out)
        assert img.size == (1600, 1200)

    def test_upscaled_image_is_larger(self, img_path):
        from imagemcp.tools.advanced_ai import upscale_image
        orig = Image.open(img_path)
        out = Image.open(upscale_image(img_path, scale_factor=2))
        assert out.width > orig.width
        assert out.height > orig.height
