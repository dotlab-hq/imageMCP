"""Tests for AI image generation tools.

All generation requires ANTHROPIC_API_KEY — skipped without it.
The tests verify return values and file validity.
"""

import os
import pytest
from PIL import Image

from imagemcp.utils.ai_client import get_client

HAS_API = get_client() is not None
pytestmark = pytest.mark.skipif(not HAS_API, reason="No ANTHROPIC_API_KEY set")


def _is_valid_image(path):
    assert os.path.exists(path), f"Missing: {path}"
    img = Image.open(path)
    assert img.size[0] > 0 and img.size[1] > 0
    return img


class TestGenerateAvatar:
    def test_default_style(self):
        from imagemcp.tools.ai_generation import generate_avatar
        out = generate_avatar("a friendly robot")
        _is_valid_image(out)

    def test_cartoon_style(self):
        from imagemcp.tools.ai_generation import generate_avatar
        out = generate_avatar("a cat wearing glasses", style="cartoon")
        _is_valid_image(out)

    def test_anime_style(self):
        from imagemcp.tools.ai_generation import generate_avatar
        out = generate_avatar("a warrior princess", style="anime")
        _is_valid_image(out)


class TestGenerateIcon:
    def test_flat_icon(self):
        from imagemcp.tools.ai_generation import generate_icon
        out = generate_icon("a shopping cart", style="flat")
        _is_valid_image(out)

    def test_3d_icon(self):
        from imagemcp.tools.ai_generation import generate_icon
        out = generate_icon("a cloud server", style="3d")
        _is_valid_image(out)

    def test_line_icon(self):
        from imagemcp.tools.ai_generation import generate_icon
        out = generate_icon("a gear settings", style="line")
        _is_valid_image(out)


class TestGenerateBackground:
    def test_default(self):
        from imagemcp.tools.ai_generation import generate_background
        out = generate_background("modern tech office")
        _is_valid_image(out)

    def test_custom_size(self):
        from imagemcp.tools.ai_generation import generate_background
        out = generate_background("sunset beach", width=768, height=512)
        _is_valid_image(out)


class TestGenerateIllustration:
    def test_default(self):
        from imagemcp.tools.ai_generation import generate_illustration
        out = generate_illustration("a city skyline at night")
        _is_valid_image(out)

    def test_minimal_style(self):
        from imagemcp.tools.ai_generation import generate_illustration
        out = generate_illustration("a tree in a park", style="minimal")
        _is_valid_image(out)


class TestGenerateCharacter:
    def test_default(self):
        from imagemcp.tools.ai_generation import generate_character
        out = generate_character("a wizard with a staff")
        _is_valid_image(out)

    def test_pixel_style(self):
        from imagemcp.tools.ai_generation import generate_character
        out = generate_character("a space explorer", style="pixel")
        _is_valid_image(out)
