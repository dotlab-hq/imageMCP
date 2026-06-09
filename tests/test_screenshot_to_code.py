"""Tests for screenshot-to-code tools.

All require ANTHROPIC_API_KEY — skipped without it.
"""

import os
import pytest
from PIL import Image

from imagemcp.utils.ai_client import get_client

HAS_API = get_client() is not None
pytestmark = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


class TestScreenshotToHtml:
    def test_returns_html(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_html
        result = screenshot_to_html(ui_path)
        assert isinstance(result, str)
        assert "<" in result  # Contains HTML tags

    def test_returns_div_structure(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_html
        result = screenshot_to_html(ui_path)
        assert "div" in result.lower() or "section" in result.lower() or "header" in result.lower()


class TestScreenshotToReact:
    def test_returns_component(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_react
        result = screenshot_to_react(ui_path)
        assert isinstance(result, str)
        assert "function" in result or "const" in result or "export" in result

    def test_returns_jsx(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_react
        result = screenshot_to_react(ui_path, styling="tailwind")
        assert "<" in result  # JSX tags


class TestScreenshotToComponentTree:
    def test_returns_dict(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_component_tree
        result = screenshot_to_component_tree(ui_path)
        assert isinstance(result, dict)

    def test_has_components(self, ui_path):
        from imagemcp.tools.screenshot_to_code import screenshot_to_component_tree
        result = screenshot_to_component_tree(ui_path)
        assert "root" in result or "components" in result


class TestImageToWireframe:
    def test_returns_html(self, ui_path):
        from imagemcp.tools.screenshot_to_code import image_to_wireframe
        result = image_to_wireframe(ui_path)
        assert isinstance(result, str)
        assert "<" in result
