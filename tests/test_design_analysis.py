"""Tests for design analysis tools.

extract_colors has a local fallback; the rest require ANTHROPIC_API_KEY.
"""

import os
import pytest
from PIL import Image

from imagemcp.utils.ai_client import get_client

HAS_API = get_client() is not None
api_skip = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


class TestExtractColors:
    def test_local_fallback(self, img_path):
        from imagemcp.tools.design_analysis import extract_colors
        colors = extract_colors(img_path, count=5)
        assert isinstance(colors, list)
        assert len(colors) <= 5
        for c in colors:
            assert "hex" in c
            assert c["hex"].startswith("#")
            assert len(c["hex"]) == 7
            assert "pct" in c
            assert 0 <= c["pct"] <= 100

    def test_different_counts(self, img_path):
        from imagemcp.tools.design_analysis import extract_colors
        c3 = extract_colors(img_path, count=3)
        c8 = extract_colors(img_path, count=8)
        assert len(c3) <= 3
        assert len(c8) <= 8

    def test_rgb_key_present(self, img_path):
        from imagemcp.tools.design_analysis import extract_colors
        colors = extract_colors(img_path, count=3)
        for c in colors:
            assert "rgb" in c
            r, g, b = c["rgb"]
            assert 0 <= r <= 255
            assert 0 <= g <= 255
            assert 0 <= b <= 255


class TestExtractTypography:
    @api_skip
    def test_returns_list(self, ui_path):
        from imagemcp.tools.design_analysis import extract_typography
        result = extract_typography(ui_path)
        assert isinstance(result, list)


class TestDetectLayout:
    @api_skip
    def test_returns_dict(self, ui_path):
        from imagemcp.tools.design_analysis import detect_layout
        result = detect_layout(ui_path)
        assert isinstance(result, dict)
        assert "sections" in result or "layout" in str(result)


class TestDescribeDesign:
    @api_skip
    def test_returns_string(self, ui_path):
        from imagemcp.tools.design_analysis import describe_design
        result = describe_design(ui_path)
        assert isinstance(result, str)
        assert len(result) > 50


class TestIdentifyComponents:
    @api_skip
    def test_returns_components(self, ui_path):
        from imagemcp.tools.design_analysis import identify_components
        result = identify_components(ui_path)
        assert isinstance(result, list)
        for comp in result:
            assert "component" in comp
            assert "bounds" in comp
