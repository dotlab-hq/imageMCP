"""AI image generation tools — avatars, icons, backgrounds, illustrations, characters."""

from imagemcp.utils.ai_client import generate_image


STYLE_PROMPTS = {
    "generate_avatar": {
        "default": "Professional avatar portrait, clean background, high quality digital art",
        "cartoon": "Cartoon-style avatar, vibrant colors, clean flat design",
        "realistic": "Photorealistic professional headshot, studio lighting",
        "anime": "Anime-style character portrait, detailed, high quality",
    },
    "generate_icon": {
        "default": "Minimal flat icon, simple geometric shapes, clean design, no text",
        "flat": "Flat design icon, solid colors, minimal detail",
        "3d": "3D rendered icon, soft lighting, modern style",
        "line": "Line art icon, thin strokes, monochrome, clean",
    },
    "generate_background": {
        "default": "Abstract background, soft gradients, modern aesthetic",
        "gradient": "Smooth color gradient background, modern and clean",
        "pattern": "Seamless pattern background, subtle texture",
        "scene": "Illustrated scene background, wide angle",
    },
    "generate_illustration": {
        "default": "High quality digital illustration, detailed, professional",
        "minimal": "Minimalist illustration, few colors, clean lines",
        "detailed": "Highly detailed illustration, rich colors, professional art",
    },
    "generate_character": {
        "default": "Character design, full body, clean background, concept art",
        "realistic": "Realistic character concept art, detailed, professional",
        "cartoon": "Cartoon character design, vibrant, fun, expressive",
        "pixel": "Pixel art character, retro style, 32x32 scaled up",
    },
}


def generate_avatar(description: str, style: str = "default") -> str:
    """Generate an avatar image from a text description with an optional style."""
    styles = STYLE_PROMPTS["generate_avatar"]
    prefix = styles.get(style, styles["default"])
    return generate_image(f"{prefix}: {description}")


def generate_icon(description: str, style: str = "default") -> str:
    """Generate an icon image from a text description with an optional style."""
    styles = STYLE_PROMPTS["generate_icon"]
    prefix = styles.get(style, styles["default"])
    return generate_image(f"{prefix}: {description}")


def generate_background(description: str, width: int = 1024, height: int = 1024) -> str:
    """Generate a background image from a text description with specified dimensions."""
    styles = STYLE_PROMPTS["generate_background"]
    prefix = styles["default"]
    size = f"{min(width, 1536)}x{min(height, 1536)}"
    return generate_image(f"{prefix}: {description}", size=size)


def generate_illustration(description: str, style: str = "default") -> str:
    """Generate an illustration from a text description with an optional style."""
    styles = STYLE_PROMPTS["generate_illustration"]
    prefix = styles.get(style, styles["default"])
    return generate_image(f"{prefix}: {description}")


def generate_character(description: str, style: str = "default") -> str:
    """Generate a character design from a text description with an optional style."""
    styles = STYLE_PROMPTS["generate_character"]
    prefix = styles.get(style, styles["default"])
    return generate_image(f"{prefix}: {description}")
