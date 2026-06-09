# ImageMcp

A full-featured **image processing MCP server** for AI assistants. Exposes ~55 tools across 11 categories — editing, layers, format conversion, AI segmentation/cleanup/generation, design analysis, screenshot-to-code, and more.

## Quick Start

```bash
# Install
pip install -e .

# Set API key (required for AI-powered tools)
export ANTHROPIC_API_KEY="sk-..."

# Run the MCP server
python server.py

# Or with the MCP CLI
mcp run server.py
```

Without `ANTHROPIC_API_KEY`, all non-AI tools work (core editing, layers, conversions) and AI tools degrade to local Pillow fallbacks with reduced quality.

## Tools

### Core Editing (10)

`crop_image`, `resize_image`, `rotate_image`, `flip_image`, `add_text`, `remove_text`, `blur_region`, `adjust_brightness`, `adjust_contrast`, `export_image`

### Layer Management (8)

`create_document`, `add_image_layer`, `add_text_layer`, `move_layer`, `resize_layer`, `delete_layer`, `duplicate_layer`, `list_layers`

### Format Conversions (7)

`png_to_jpg`, `jpg_to_png`, `webp_to_png`, `svg_to_png`, `png_to_svg`, `image_to_pdf`, `pdf_to_images`

### AI Segmentation & Selection (6)

`extract_subject`, `extract_person`, `extract_face`, `extract_object`, `remove_background`, `generate_mask`

### AI Cleanup (4)

`remove_object`, `erase_text`, `remove_watermark_candidate`, `inpaint_region`

### AI Generation (5)

`generate_avatar`, `generate_icon`, `generate_background`, `generate_illustration`, `generate_character`

### Design Analysis (5)

`extract_colors`, `extract_typography`, `detect_layout`, `describe_design`, `identify_components`

### Screenshot → Code (4)

`screenshot_to_html`, `screenshot_to_react`, `screenshot_to_component_tree`, `image_to_wireframe`

### Smart Export (5)

`export_png`, `export_svg`, `export_react`, `export_tailwind`, `export_figma_json`

### Advanced AI (7)

`photo_to_headshot`, `photo_to_cartoon`, `photo_to_vector`, `photo_to_3d`, `style_transfer`, `face_enhancement`, `upscale_image`

## Architecture

```
D:\ImageMcp\
├── server.py                    # FastMCP entry — registers all 55 tools
├── main.py                      # CLI entry point
├── pyproject.toml               # Python project config + dependencies
│
├── src/imagemcp/
│   ├── tools/                   # One module per tool category
│   │   ├── core_editing.py
│   │   ├── layers.py
│   │   ├── conversions.py
│   │   ├── ai_segmentation.py
│   │   ├── ai_cleanup.py
│   │   ├── ai_generation.py
│   │   ├── design_analysis.py
│   │   ├── screenshot_to_code.py
│   │   ├── smart_export.py
│   │   └── advanced_ai.py
│   │
│   └── utils/
│       ├── io.py                # Image I/O, temp file management
│       ├── ai_client.py         # Anthropic SDK client, vision helpers, image generation
│       └── canvas.py            # In-memory layer canvas for compositing
│
└── tests/                       # ~120 tests across all tool categories
    ├── conftest.py
    └── test_*.py
```

## Configuration

| Variable            | Purpose                                            |
| ------------------- | -------------------------------------------------- |
| `ANTHROPIC_API_KEY` | Required for AI vision/generation/inpainting tools |
| `IMAGEMCP_STORAGE`  | Custom temp directory (default: system temp)       |

## Connecting to the Server

Once the server is running, any MCP-compatible client can connect via **stdio** transport.

### Claude Desktop / Claude Code

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ImageMcp": {
      "command": "python",
      "args": ["D:/ImageMCP/server.py"]
    }
  }
}
```

### VS Code (GitHub Copilot)

Create or edit `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "ImageMcp": {
      "type": "stdio",
      "command": "python",
      "args": ["D:/ImageMCP/server.py"]
    }
  }
}
```

### Using UV

If you use `uv` to manage the project:

```json
{
  "mcpServers": {
    "ImageMcp": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "D:/ImageMCP"
    }
  }
}
```

### Custom MCP Client (stdio)

The server communicates over **stdin/stdout** using the Model Context Protocol (MCP) JSON-RPC format. Any MCP-compatible client can connect — no HTTP server needed.

## Development

```bash
# Install dev dependencies
pip install -e ".[test]"

# Download test assets
python -m tests.download_assets

# Run tests (API tests auto-skip if ANTHROPIC_API_KEY not set)
pytest tests/ -v
```

## Stack

- **MCP framework:** `mcp[cli]` (FastMCP)
- **Image processing:** Pillow, numpy
- **AI:** Anthropic Claude SDK (vision, image generation, inpainting)
- **Background removal:** rembg (U²-Net, runs locally)
- **Format support:** cairosvg, PyMuPDF, reportlab
- **OCR:** pytesseract (optional)
