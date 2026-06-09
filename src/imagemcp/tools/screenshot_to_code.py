"""Screenshot-to-code tools — convert UI images to HTML, React, component trees, wireframes."""

from imagemcp.utils.ai_client import vision_describe, vision_json


def screenshot_to_html(image_path: str, framework: str = "html") -> str:
    """Convert a screenshot to clean HTML + CSS."""
    return vision_describe(
        image_path,
        "Convert this UI screenshot to clean, semantic HTML with inline CSS. "
        "Use modern CSS (flexbox/grid where appropriate). Include realistic placeholder text. "
        "Output ONLY the HTML code, no explanation."
    )


def screenshot_to_react(image_path: str, styling: str = "tailwind") -> str:
    """Convert a screenshot to a React component."""
    style_instruction = (
        "Use Tailwind CSS classes" if styling == "tailwind"
        else "Use CSS modules with a .module.css approach"
    )
    return vision_describe(
        image_path,
        f"Convert this UI screenshot to a React component. {style_instruction}. "
        "Use TypeScript. Include realistic placeholder data. "
        "Output ONLY the component code, no explanation. "
        "Use proper JSX structure with semantic HTML elements."
    )


def screenshot_to_component_tree(image_path: str) -> dict:
    """Analyze screenshot and return a structured component hierarchy."""
    return vision_json(
        image_path,
        "Analyze this UI screenshot and decompose it into a component tree. Return JSON:\n"
        '{"root": str, "components": [{"name": str, "type": str, "props": {}, '
        '"children": [...]}]}\n'
        "Each component should have: name, type (div/section/button/input/etc), "
        "props (class, text content, etc), and nested children."
    )


def image_to_wireframe(image_path: str) -> str:
    """Convert a screenshot to a simplified wireframe."""
    return vision_describe(
        image_path,
        "Convert this UI design into a wireframe HTML page. Use only:\n"
        "- Gray rectangles for images/content blocks\n"
        "- Single lines for text\n"
        "- Simple borders for containers\n"
        "No colors, no images, no detailed styling. Just layout structure. "
        "Output ONLY the HTML wireframe code."
    )
