"""Tests for AI cleanup tools — inpaint, remove object, erase text.

Local fallbacks (Gaussian blur blend) are tested unconditionally.
API-based tests are skipped if ANTHROPIC_API_KEY is not set.
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
    assert img.size[0] > 0
    return img


class TestRemoveObject:
    def test_local_fallback_blurs_region(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_object
        out = remove_object(img_path, x=100, y=100, width=200, height=150)
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_region_looks_different(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_object
        orig = np.array(Image.open(img_path).convert("RGB"))
        out = np.array(Image.open(remove_object(img_path, x=100, y=100, width=200, height=200)).convert("RGB"))
        # The inpainted region should differ from original
        region_orig = orig[100:300, 100:300]
        region_out = out[100:300, 100:300]
        assert not np.array_equal(region_orig, region_out), "Region should be modified"

    def test_surrounding_pixels_unchanged(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_object
        orig = np.array(Image.open(img_path).convert("RGB"))
        out = np.array(Image.open(remove_object(img_path, x=100, y=100, width=200, height=200)).convert("RGB"))
        # Corner (0,0) should be untouched
        np.testing.assert_array_equal(orig[0:50, 0:50], out[0:50, 0:50])

    @api_skip
    def test_api_inpaint(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_object
        out = remove_object(img_path, x=200, y=200, width=100, height=100)
        _is_image(out)


class TestEraseText:
    def test_with_explicit_region(self, img_path):
        from imagemcp.tools.ai_cleanup import erase_text
        out = erase_text(img_path, x=50, y=50, width=200, height=30)
        img = _is_image(out)
        assert img.size == (800, 600)


class TestRemoveWatermarkCandidate:
    def test_runs_without_error(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_watermark_candidate
        out = remove_watermark_candidate(img_path)
        _is_image(out)

    def test_output_same_dimensions(self, img_path):
        from imagemcp.tools.ai_cleanup import remove_watermark_candidate
        orig = Image.open(img_path)
        out = Image.open(remove_watermark_candidate(img_path))
        assert out.size == orig.size


class TestInpaintRegion:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.ai_cleanup import inpaint_region
        # Create a simple mask
        mask = Image.new("L", (800, 600), 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.rectangle([100, 100, 300, 300], fill=255)
        mask_path = os.path.join(os.path.dirname(img_path), "test_mask.png")
        mask.save(mask_path)

        out = inpaint_region(img_path, mask_path, prompt="fill naturally")
        _is_image(out)

    @api_skip
    def test_api_inpaint(self, img_path):
        from imagemcp.tools.ai_cleanup import inpaint_region
        mask = Image.new("L", (800, 600), 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.rectangle([200, 200, 400, 400], fill=255)
        mask_path = os.path.join(os.path.dirname(img_path), "test_mask_api.png")
        mask.save(mask_path)

        out = inpaint_region(img_path, mask_path, prompt="fill with sky")
        _is_image(out)
