"""ImageMcp — MCP server exposing ~55 image processing tools to LLMs."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "ImageMcp",
    instructions="Full-featured image processing MCP server: editing, layers, conversions, AI segmentation/cleanup/generation, design analysis, screenshot-to-code, and smart export.",
)

# ──────────────────────────────────────────────
# Core Editing
# ──────────────────────────────────────────────
from imagemcp.tools.core_editing import (
    crop_image, resize_image, rotate_image, flip_image,
    add_text, remove_text, blur_region,
    adjust_brightness, adjust_contrast, export_image,
)

mcp.tool()(crop_image)
mcp.tool()(resize_image)
mcp.tool()(rotate_image)
mcp.tool()(flip_image)
mcp.tool()(add_text)
mcp.tool()(remove_text)
mcp.tool()(blur_region)
mcp.tool()(adjust_brightness)
mcp.tool()(adjust_contrast)
mcp.tool()(export_image)

# ──────────────────────────────────────────────
# Layer Management
# ──────────────────────────────────────────────
from imagemcp.tools.layers import (
    create_document, add_image_layer, add_text_layer,
    move_layer, resize_layer, delete_layer, duplicate_layer, list_layers,
)

mcp.tool()(create_document)
mcp.tool()(add_image_layer)
mcp.tool()(add_text_layer)
mcp.tool()(move_layer)
mcp.tool()(resize_layer)
mcp.tool()(delete_layer)
mcp.tool()(duplicate_layer)
mcp.tool()(list_layers)

# ──────────────────────────────────────────────
# Conversions
# ──────────────────────────────────────────────
from imagemcp.tools.conversions import (
    png_to_jpg, jpg_to_png, webp_to_png, svg_to_png,
    png_to_svg, image_to_pdf, pdf_to_images,
)

mcp.tool()(png_to_jpg)
mcp.tool()(jpg_to_png)
mcp.tool()(webp_to_png)
mcp.tool()(svg_to_png)
mcp.tool()(png_to_svg)
mcp.tool()(image_to_pdf)
mcp.tool()(pdf_to_images)

# ──────────────────────────────────────────────
# AI Segmentation & Selection
# ──────────────────────────────────────────────
from imagemcp.tools.ai_segmentation import (
    extract_subject, extract_person, extract_face,
    extract_object, remove_background, generate_mask,
)

mcp.tool()(extract_subject)
mcp.tool()(extract_person)
mcp.tool()(extract_face)
mcp.tool()(extract_object)
mcp.tool()(remove_background)
mcp.tool()(generate_mask)

# ──────────────────────────────────────────────
# AI Cleanup
# ──────────────────────────────────────────────
from imagemcp.tools.ai_cleanup import (
    remove_object, erase_text, remove_watermark_candidate, inpaint_region,
)

mcp.tool()(remove_object)
mcp.tool()(erase_text)
mcp.tool()(remove_watermark_candidate)
mcp.tool()(inpaint_region)

# ──────────────────────────────────────────────
# AI Generation
# ──────────────────────────────────────────────
from imagemcp.tools.ai_generation import (
    generate_avatar, generate_icon, generate_background,
    generate_illustration, generate_character,
)

mcp.tool()(generate_avatar)
mcp.tool()(generate_icon)
mcp.tool()(generate_background)
mcp.tool()(generate_illustration)
mcp.tool()(generate_character)

# ──────────────────────────────────────────────
# Design Analysis
# ──────────────────────────────────────────────
from imagemcp.tools.design_analysis import (
    extract_colors, extract_typography, detect_layout,
    describe_design, identify_components,
)

mcp.tool()(extract_colors)
mcp.tool()(extract_typography)
mcp.tool()(detect_layout)
mcp.tool()(describe_design)
mcp.tool()(identify_components)

# ──────────────────────────────────────────────
# Screenshot to Code
# ──────────────────────────────────────────────
from imagemcp.tools.screenshot_to_code import (
    screenshot_to_html, screenshot_to_react,
    screenshot_to_component_tree, image_to_wireframe,
)

mcp.tool()(screenshot_to_html)
mcp.tool()(screenshot_to_react)
mcp.tool()(screenshot_to_component_tree)
mcp.tool()(image_to_wireframe)

# ──────────────────────────────────────────────
# Smart Export
# ──────────────────────────────────────────────
from imagemcp.tools.smart_export import (
    export_png, export_svg, export_react, export_tailwind, export_figma_json,
)

mcp.tool()(export_png)
mcp.tool()(export_svg)
mcp.tool()(export_react)
mcp.tool()(export_tailwind)
mcp.tool()(export_figma_json)

# ──────────────────────────────────────────────
# Advanced AI Features
# ──────────────────────────────────────────────
from imagemcp.tools.advanced_ai import (
    photo_to_headshot, photo_to_cartoon, photo_to_vector,
    photo_to_3d, style_transfer, face_enhancement, upscale_image,
)

mcp.tool()(photo_to_headshot)
mcp.tool()(photo_to_cartoon)
mcp.tool()(photo_to_vector)
mcp.tool()(photo_to_3d)
mcp.tool()(style_transfer)
mcp.tool()(face_enhancement)
mcp.tool()(upscale_image)


if __name__ == "__main__":
    mcp.run()
