"""Tests for AI segmentation tools.

These tools use rembg (local) and OpenAI vision (API).
All tests verify that local fallbacks work; API tests are skipped if no key.
"""

import os
import pytest
from PIL import Image

from imagemcp.utils.ai_client import get_client

HAS_API = get_client() is not None
api_skip = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


def _is_image(path):
    assert os.path.exists(path), f"Missing: {path}"
    img = Image.open(path)
    assert img.size[0] > 0 and img.size[1] > 0
    return img


def _has_alpha(path):
    img = Image.open(path)
    return img.mode == "RGBA"


class TestExtractSubject:
    def test_basic(self, img_path):
        from imagemcp.tools.ai_segmentation import extract_subject
        out = extract_subject(img_path)
        img = _is_image(out)
        assert img.mode == "RGBA"

    def test_removes_background(self, img_path):
        from imagemcp.tools.ai_segmentation import extract_subject
        out = extract_subject(img_path)
        img = Image.open(out)
        alpha = img.split()[3]
        # There should be at least some transparent pixels
        extrema = alpha.getextrema()
        assert extrema[0] < 255, "Expected some transparent pixels after bg removal"


class TestExtractPerson:
    def test_basic(self, portrait_path):
        from imagemcp.tools.ai_segmentation import extract_person
        out = extract_person(portrait_path)
        img = _is_image(out)
        assert img.mode == "RGBA"


class TestExtractFace:
    def test_returns_list(self, portrait_path):
        from imagemcp.tools.ai_segmentation import extract_face
        out = extract_face(portrait_path)
        assert isinstance(out, list)
        assert len(out) >= 1
        for p in out:
            _is_image(p)


class TestRemoveBackground:
    def test_basic(self, img_path):
        from imagemcp.tools.ai_segmentation import remove_background
        out = remove_background(img_path)
        img = _is_image(out)
        assert img.mode == "RGBA"


class TestExtractObject:
    @api_skip
    def test_extract_named_object(self, landscape_path):
        from imagemcp.tools.ai_segmentation import extract_object
        out = extract_object(landscape_path, description="the sky")
        img = _is_image(out)
        assert img.mode == "RGBA"


class TestGenerateMask:
    @api_skip
    def test_basic_mask(self, img_path):
        from imagemcp.tools.ai_segmentation import generate_mask
        out = generate_mask(img_path, description="the center of the image")
        img = _is_image(out)
        # Mask should be grayscale
        assert img.mode == "L"
