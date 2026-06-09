"""Tests for smart export tools.

Most are local-only; export_react/export_tailwind/export_figma_json need API.
"""

import os
import json
import pytest
from PIL import Image

from imagemcp.utils.ai_client import get_client
from imagemcp.tools.layers import create_document, add_image_layer, add_text_layer

HAS_API = get_client() is not None
api_skip = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


def _exists(path):
    assert os.path.exists(path), f"Missing: {path}"


def _make_doc(img_path):
    doc = create_document(800, 600)
    add_image_layer(doc, img_path, x=0, y=0)
    add_text_layer(doc, "Export Test", x=50, y=50)
    return doc


class TestExportPng:
    def test_from_document(self, img_path):
        from imagemcp.tools.smart_export import export_png
        doc = _make_doc(img_path)
        out = export_png(document_id=doc)
        _exists(out)
        img = Image.open(out)
        assert img.size == (800, 600)

    def test_from_image(self, img_path):
        from imagemcp.tools.smart_export import export_png
        out = export_png(image_path=img_path)
        _exists(out)

    def test_no_args_raises(self):
        from imagemcp.tools.smart_export import export_png
        with pytest.raises(ValueError):
            export_png()


class TestExportSvg:
    def test_from_document(self, img_path):
        from imagemcp.tools.smart_export import export_svg
        doc = _make_doc(img_path)
        out = export_svg(document_id=doc)
        _exists(out)
        content = open(out).read()
        assert "<svg" in content

    def test_from_image(self, img_path):
        from imagemcp.tools.smart_export import export_svg
        out = export_svg(image_path=img_path)
        _exists(out)
        content = open(out).read()
        assert "data:image/png;base64" in content


class TestExportReact:
    @api_skip
    def test_returns_component(self, img_path):
        from imagemcp.tools.smart_export import export_react
        result = export_react(image_path=img_path)
        assert isinstance(result, str)
        assert "function" in result or "const" in result or "export" in result


class TestExportTailwind:
    @api_skip
    def test_returns_html(self, img_path):
        from imagemcp.tools.smart_export import export_tailwind
        result = export_tailwind(image_path=img_path)
        assert isinstance(result, str)
        assert "<" in result


class TestExportFigmaJson:
    @api_skip
    def test_returns_structure(self, img_path):
        from imagemcp.tools.smart_export import export_figma_json
        result = export_figma_json(image_path=img_path)
        assert isinstance(result, dict)
        assert "canvas_layers" in result
        assert "nodes" in result
