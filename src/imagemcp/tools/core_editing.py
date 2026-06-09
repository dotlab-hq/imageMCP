"""Core image editing tools — crop, resize, rotate, flip, text, blur, brightness, contrast."""

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
from imagemcp.utils.io import load_image, save_image


def crop_image(image_path: str, x: int, y: int, width: int, height: int) -> str:
    """Crop an image to a specified rectangular region."""
    img = load_image(image_path)
    cropped = img.crop((x, y, x + width, y + height))
    return save_image(cropped)


def resize_image(image_path: str, width: int, height: int | None = None, maintain_aspect: bool = True) -> str:
    """Resize an image to the given width and height, optionally maintaining aspect ratio."""
    img = load_image(image_path)
    if maintain_aspect and height is None:
        ratio = width / img.width
        height = int(img.height * ratio)
    elif height is None:
        height = img.height
    resized = img.resize((width, height), Image.LANCZOS)
    return save_image(resized)


def rotate_image(image_path: str, angle: float, expand: bool = True) -> str:
    """Rotate an image by a given angle in degrees."""
    img = load_image(image_path)
    rotated = img.rotate(-angle, expand=expand, resample=Image.BICUBIC)
    return save_image(rotated)


def flip_image(image_path: str, direction: str = "horizontal") -> str:
    """Flip an image horizontally, vertically, or both."""
    img = load_image(image_path)
    if direction == "horizontal":
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif direction == "vertical":
        flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
    elif direction == "both":
        flipped = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.FLIP_TOP_BOTTOM)
    else:
        raise ValueError(f"Invalid direction: {direction}")
    return save_image(flipped)


def add_text(image_path: str, text: str, x: int, y: int, font_size: int = 24, color: str = "#000000", font_family: str | None = None) -> str:
    """Add text to an image at the specified position with given font settings."""
    img = load_image(image_path)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(font_family or "arial.ttf", font_size)
    except (OSError, IOError):
        font = ImageFont.load_default()
    draw.text((x, y), text, fill=color, font=font)
    return save_image(img)


def remove_text(image_path: str, x: int, y: int, width: int, height: int) -> str:
    """Remove text from a region by blurring the area to obscure it."""
    img = load_image(image_path)
    # Use surrounding colors to fill (simple inpaint: average border color)
    region = img.crop((x, y, x + width, y + height))
    # Blur the region to remove text while keeping structure
    blurred = region.filter(ImageFilter.GaussianBlur(radius=15))
    img.paste(blurred, (x, y))
    return save_image(img)


def blur_region(image_path: str, x: int, y: int, width: int, height: int, radius: int = 10) -> str:
    """Apply Gaussian blur to a rectangular region of the image."""
    img = load_image(image_path)
    region = img.crop((x, y, x + width, y + height))
    blurred = region.filter(ImageFilter.GaussianBlur(radius=radius))
    img.paste(blurred, (x, y))
    return save_image(img)


def adjust_brightness(image_path: str, factor: float = 1.0) -> str:
    """Adjust image brightness. Factor > 1 brightens, < 1 darkens."""
    img = load_image(image_path)
    enhancer = ImageEnhance.Brightness(img)
    result = enhancer.enhance(factor)
    return save_image(result)


def adjust_contrast(image_path: str, factor: float = 1.0) -> str:
    """Adjust image contrast. Factor > 1 increases contrast, < 1 decreases it."""
    img = load_image(image_path)
    enhancer = ImageEnhance.Contrast(img)
    result = enhancer.enhance(factor)
    return save_image(result)


def export_image(image_path: str, format: str = "png", quality: int = 95) -> str:
    """Export an image in the specified format (png, jpg, webp, etc.)."""
    img = load_image(image_path)
    return save_image(img, ext=format.lower())
