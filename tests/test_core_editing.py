"""Tests for core image editing tools."""

import os
import pytest
from PIL import Image

from imagemcp.tools.core_editing import (
    crop_image,
    resize_image,
    rotate_image,
    flip_image,
    add_text,
    remove_text,
    blur_region,
    adjust_brightness,
    adjust_contrast,
    export_image,
)


def _open(path):
    return Image.open(path)


def _exists(path):
    assert os.path.exists(path), f"Output file missing: {path}"


def _is_image(path):
    _exists(path)
    img = _open(path)
    assert img.size[0] > 0 and img.size[1] > 0
    return img


class TestCropImage:
    def test_basic_crop(self, img_path):
        out = crop_image(img_path, x=0, y=0, width=400, height=300)
        img = _is_image(out)
        assert img.size == (400, 300)

    def test_crop_center(self, img_path):
        out = crop_image(img_path, x=200, y=150, width=200, height=200)
        img = _is_image(out)
        assert img.size == (200, 200)

    def test_crop_preserves_content(self, img_path):
        out = crop_image(img_path, x=0, y=0, width=800, height=600)
        img = _is_image(out)
        assert img.size == (800, 600)


class TestResizeImage:
    def test_resize_to_half(self, img_path):
        out = resize_image(img_path, width=400, height=300)
        img = _is_image(out)
        assert img.size == (400, 300)

    def test_resize_width_only_maintains_aspect(self, img_path):
        out = resize_image(img_path, width=400, maintain_aspect=True)
        img = _is_image(out)
        assert img.size[0] == 400
        assert img.size[1] == 300  # 600 * (400/800)

    def test_resize_no_aspect(self, img_path):
        out = resize_image(img_path, width=500, height=500, maintain_aspect=False)
        img = _is_image(out)
        assert img.size == (500, 500)

    def test_resize_upscale(self, img_path):
        out = resize_image(img_path, width=1600, height=1200)
        img = _is_image(out)
        assert img.size == (1600, 1200)


class TestRotateImage:
    def test_rotate_90(self, img_path):
        out = rotate_image(img_path, angle=90)
        img = _is_image(out)
        assert img.size == (600, 800)  # swapped with expand=True

    def test_rotate_0(self, img_path):
        out = rotate_image(img_path, angle=0)
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_rotate_45(self, img_path):
        out = rotate_image(img_path, angle=45, expand=True)
        img = _is_image(out)
        assert img.size[0] > 800  # expanded

    def test_rotate_no_expand(self, img_path):
        out = rotate_image(img_path, angle=90, expand=False)
        img = _is_image(out)
        assert img.size == (800, 600)  # same bounding box


class TestFlipImage:
    def test_flip_horizontal(self, img_path):
        out = flip_image(img_path, direction="horizontal")
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_flip_vertical(self, img_path):
        out = flip_image(img_path, direction="vertical")
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_flip_both(self, img_path):
        out = flip_image(img_path, direction="both")
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_flip_invalid_direction(self, img_path):
        with pytest.raises(ValueError, match="Invalid direction"):
            flip_image(img_path, direction="diagonal")


class TestAddText:
    def test_add_text_default(self, img_path):
        out = add_text(img_path, text="Hello World", x=100, y=100)
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_add_text_large_font(self, img_path):
        out = add_text(img_path, text="BIG", x=50, y=50, font_size=72, color="#ff0000")
        img = _is_image(out)
        assert img.size[0] > 0

    def test_add_text_small(self, img_path):
        out = add_text(img_path, text="tiny", x=0, y=0, font_size=12)
        _is_image(out)


class TestRemoveText:
    def test_remove_text_region(self, img_path):
        out = remove_text(img_path, x=100, y=100, width=200, height=50)
        img = _is_image(out)
        assert img.size == (800, 600)


class TestBlurRegion:
    def test_blur_basic(self, img_path):
        out = blur_region(img_path, x=0, y=0, width=200, height=200, radius=10)
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_blur_high_radius(self, img_path):
        out = blur_region(img_path, x=100, y=100, width=300, height=200, radius=50)
        _is_image(out)


class TestBrightnessContrast:
    def test_brighten(self, img_path):
        out = adjust_brightness(img_path, factor=1.5)
        img = _is_image(out)
        assert img.size == (800, 600)

    def test_darken(self, img_path):
        out = adjust_brightness(img_path, factor=0.5)
        _is_image(out)

    def test_no_change(self, img_path):
        out = adjust_brightness(img_path, factor=1.0)
        _is_image(out)

    def test_contrast_up(self, img_path):
        out = adjust_contrast(img_path, factor=2.0)
        _is_image(out)

    def test_contrast_down(self, img_path):
        out = adjust_contrast(img_path, factor=0.5)
        _is_image(out)


class TestExportImage:
    def test_export_jpg(self, img_path):
        out = export_image(img_path, format="jpg", quality=80)
        img = _is_image(out)
        assert img.format == "JPEG" or out.endswith(".jpg")

    def test_export_webp(self, img_path):
        out = export_image(img_path, format="webp")
        _is_image(out)

    def test_export_png(self, img_path):
        out = export_image(img_path, format="png")
        img = _is_image(out)
        assert out.endswith(".png")
