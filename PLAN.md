# ImageMcp — Full-Featured Image Processing MCP Server

## Vision

Build a Python MCP server (`mcp` with `FastMCP`) that exposes ~50 tools covering every major image operation an LLM assistant could need: editing, layers, conversion, AI segmentation/cleanup/generation, design analysis, screenshot-to-code, and smart export.

**Stack:** Python 3.14 · FastMCP (official MCP SDK) · Pillow · rembg · openai (for vision/GPT-image) · PyMuPDF · reportlab · cairosvg · pydantic

---

## Architecture

```
imagemcp/
├── server.py              # FastMCP server entry, registers all tools
├── pyproject.toml         # dependencies
├── PLAN.md
│
├── tools/                 # Each file = one tool category
│   ├── __init__.py
│   ├── core_editing.py    # crop, resize, rotate, flip, text, blur, brightness, contrast, export
│   ├── layers.py          # document model: layers, create, add, move, resize, delete, duplicate, list
│   ├── conversions.py     # png↔jpg, webp→png, svg→png, png→svg, image→pdf, pdf→images
│   ├── ai_segmentation.py # extract_subject, extract_person, extract_face, extract_object, remove_bg, generate_mask
│   ├── ai_cleanup.py      # remove_object, erase_text, inpaint_region
│   ├── ai_generation.py   # generate_avatar, generate_icon, generate_background, generate_illustration, generate_character
│   ├── design_analysis.py # extract_colors, extract_typography, detect_layout, describe_design, identify_components
│   ├── screenshot_to_code.py # screenshot_to_html, screenshot_to_react, screenshot_to_component_tree, image_to_wireframe
│   ├── advanced_ai.py     # photo_to_headshot, photo_to_cartoon, photo_to_vector, photo_to_3d, style_transfer, face_enhancement, upscale
│   └── smart_export.py    # export_png, export_svg, export_react, export_tailwind, export_figma_json
│
├── utils/
│   ├── __init__.py
│   ├── io.py              # load_image, save_image, temp_path helpers
│   ├── ai_client.py       # shared OpenAI client, retry logic, vision helpers
│   └── canvas.py          # in-memory layer canvas (Pillow composite engine)
│
└── tests/
    └── ...                # pytest tests per tool category
```

---

## Phases

### Phase 1 — Scaffold & Infrastructure
> Get the MCP server running with FastMCP, set up project structure, dependencies, and shared utilities.

**Deliverables:**
- `pyproject.toml` with all dependencies listed
- `server.py`: FastMCP instance, registers placeholder tools from each `tools/*.py`
- `utils/io.py`: `load_image(path) → PIL.Image`, `save_image(img, path) → str`, temp file management
- `utils/ai_client.py`: lazy OpenAI client init, helper for vision API calls (encode image → base64 → send)
- `utils/canvas.py`: `Canvas` class — manages a list of `Layer` objects, each with PIL.Image + position, supports flatten/composite
- Basic smoke test: server starts, tools are listed via `mcp list_tools`

**Verify:** `python server.py` starts without error; `mcp list_tools` shows all ~50 tool names.

---

### Phase 2 — Core Editing Tools (10 tools)
> Pure Pillow operations. No AI. These are the foundation.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `crop_image` | image_path, x, y, width, height | path to cropped PNG |
| `resize_image` | image_path, width, height?, maintain_aspect? | path to resized PNG |
| `rotate_image` | image_path, angle, expand? | path to rotated PNG |
| `flip_image` | image_path, direction (horizontal/vertical/both) | path to flipped PNG |
| `add_text` | image_path, text, x, y, font_size?, color?, font_family? | path to annotated PNG |
| `remove_text` | image_path, region (x,y,w,h) | path with region inpainted |
| `blur_region` | image_path, x, y, width, height, radius? | path with blurred region |
| `adjust_brightness` | image_path, factor (0.5=darken, 1.5=brighten) | path to adjusted PNG |
| `adjust_contrast` | image_path, factor | path to adjusted PNG |
| `export_image` | image_path, format (png/jpg/webp), quality? | path to exported file |

**Verify:** Unit tests for each tool with a test image. Edge cases: out-of-bounds crop, zero dimensions, unsupported format.

---

### Phase 3 — Layer Management (8 tools)
> In-memory canvas model. All operations happen on a `Canvas` object stored per-session (or per-file).

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `create_document` | width, height, background_color? | document_id |
| `add_image_layer` | document_id, image_path, x?, y?, name? | layer_id |
| `add_text_layer` | document_id, text, x, y, font_size?, color?, name? | layer_id |
| `move_layer` | document_id, layer_id, x, y | confirmation |
| `resize_layer` | document_id, layer_id, width, height? | confirmation |
| `delete_layer` | document_id, layer_id | confirmation |
| `duplicate_layer` | document_id, layer_id | new layer_id |
| `list_layers` | document_id | ordered layer list with metadata |

**Canvas engine:** `Canvas` holds `List[Layer]`, each `Layer` = `{id, name, PIL.Image, position, size}`. Flatten = paste each layer top-to-bottom. Export = flatten → save.

**Verify:** Create doc → add 2 image layers → move one → list → export → confirm output is correct composite.

---

### Phase 4 — Conversion Tools (7 tools)
> Format conversions. Straightforward but important for interoperability.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `png_to_jpg` | image_path, background_color? (for alpha) | path to JPG |
| `jpg_to_png` | image_path | path to PNG |
| `webp_to_png` | image_path | path to PNG |
| `svg_to_png` | image_path, width?, height? | path to PNG |
| `png_to_svg` | image_path | path to SVG |
| `image_to_pdf` | image_paths (list) | path to PDF |
| `pdf_to_images` | pdf_path, dpi? | list of paths (one per page) |

**Verify:** Round-trip tests (png→jpg→png should preserve dimensions). SVG rasterization test. Multi-page PDF test.

---

### Phase 5 — AI Segmentation & Selection (6 tools)
> Uses `rembg` (U²-Net) for background removal, plus OpenAI vision API for object/face/person detection.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `extract_subject` | image_path | path to PNG with background removed |
| `extract_person` | image_path | path to PNG, only people |
| `extract_face` | image_path | list of face crop paths |
| `extract_object` | image_path, description (text prompt) | path to PNG with described object isolated |
| `remove_background` | image_path | alias/specialization of extract_subject |
| `generate_mask` | image_path, description | path to binary mask PNG |

**Approach:**
- `remove_background` / `extract_subject`: `rembg.remove()` — fast, local, no API.
- `extract_face`: `rembg` + face detection via `pillow` cascade or OpenCV's Haar cascade (bundled).
- `extract_person`: rembg subject mask + OpenAI vision to confirm it's a person (fallback: use rembg's alpha directly).
- `extract_object`: GPT-4o vision to get bounding box → crop → rembg on crop → composite back.
- `generate_mask`: rembg alpha channel or GPT-4o vision for complex masks.

**Verify:** Test on stock photos. Check alpha channel correctness. Measure latency.

---

### Phase 6 — AI Cleanup (4 tools)
> Remove/replace content in images. Uses OpenAI's image editing API (GPT-image / DALL-E inpainting) or local fallback.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `remove_object` | image_path, x, y, width, height | path with region inpainted |
| `erase_text` | image_path, region? (auto-detect if omitted) | path with text removed |
| `remove_watermark_candidate` | image_path | path with likely watermark region removed |
| `inpaint_region` | image_path, mask_path, prompt? | path with inpainted region |

**Approach:**
- Primary: OpenAI image edit API (`images.edit` with mask).
- Fallback for `remove_object`: Pillow blur + blend (less pretty but no API needed).
- `erase_text`: OCR (pytesseract or EasyOCR) to find text bounding boxes → inpaint those regions.
- `remove_watermark_candidate`: heuristic (semi-transparent overlay detection) → inpaint.

**Verify:** Test inpainting on sample images. Check that surrounding pixels remain intact.

---

### Phase 7 — AI Generation (5 tools)
> Generate new images from prompts. Uses GPT-image-1 (OpenAI) or DALL-E 3.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `generate_avatar` | description, style? (cartoon/realistic/anime) | path to generated PNG |
| `generate_icon` | description, style? (flat/3d/line) | path to generated PNG |
| `generate_background` | description, width?, height? | path to generated PNG |
| `generate_illustration` | description, style? | path to generated PNG |
| `generate_character` | description, style? | path to generated PNG |

**Approach:** All call `openai.images.generate()` with carefully crafted system prompts per tool (e.g., `generate_icon` appends "isolated icon on transparent background, flat design"). Returns are saved to temp files.

**Verify:** Generate one of each. Check dimensions, format, that prompts are being enriched properly.

---

### Phase 8 — Design Analysis (5 tools)
> Analyze UI/design images. Uses GPT-4o vision for structured analysis.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `extract_colors` | image_path, count? | list of hex colors + percentages |
| `extract_typography` | image_path | list of font families, sizes, weights |
| `detect_layout` | image_path | structured layout description (grid, sections, alignment) |
| `describe_design` | image_path | natural language design summary |
| `identify_components` | image_path | list of UI components (button, card, nav, etc.) with bounding boxes |

**Approach:** All use GPT-4o vision with structured output (JSON mode). System prompts carefully tuned per tool to get clean JSON back. `extract_colors` also has a local fallback using Pillow's quantize.

**Verify:** Test on Figma screenshots. Check JSON structure matches expected schema.

---

### Phase 9 — Screenshot to Code (4 tools)
> Convert UI screenshots into code. High-value, complex.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `screenshot_to_html` | image_path, framework? (html/css only) | HTML string |
| `screenshot_to_react` | image_path, styling? (tailwind/css-modules) | React component string |
| `screenshot_to_component_tree` | image_path | JSON tree of component hierarchy |
| `image_to_wireframe` | image_path | wireframe SVG or HTML |

**Approach:** GPT-4o vision with code-generation system prompts. `screenshot_to_component_tree` returns structured JSON. `image_to_wireframe` uses vision to detect UI elements → outputs simplified wireframe (boxes + labels).

**Verify:** Test on common UI patterns (login page, dashboard card, nav bar). Check output is syntactically valid.

---

### Phase 10 — Smart Export (5 tools)
> Export canvas/image to various developer formats.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `export_png` | document_id or image_path | path to PNG |
| `export_svg` | document_id or image_path | SVG string or path |
| `export_react` | document_id or image_path | React component (uses layers as props) |
| `export_tailwind` | document_id or image_path | HTML + Tailwind class string |
| `export_figma_json` | document_id or image_path | Figma-compatible JSON structure |

**Approach:**
- `export_png`: Flatten canvas → save.
- `export_svg`: Pillow image → base64 SVG with embedded raster, or trace if requested.
- `export_react`: Read layers → generate React component that reconstructs the layout.
- `export_tailwind`: Same, but output divs with Tailwind classes.
- `export_figma_json`: Map layers to Figma node structure (rectangle, text, group nodes).

**Verify:** Test exports render correctly. React/Tailwind output should be syntactically valid.

---

### Phase 11 — Advanced AI Features (7 tools)
> Photo transformations. Heavy API usage.

**Tools to implement:**

| Tool | Key Params | Returns |
|------|-----------|---------|
| `photo_to_headshot` | image_path | path to professional headshot |
| `photo_to_cartoon` | image_path, style? | path to cartoon version |
| `photo_to_vector` | image_path | SVG path |
| `photo_to_3d` | image_path | path to 3D-look render |
| `style_transfer` | image_path, style_image_path or style_name | path to stylized image |
| `face_enhancement` | image_path | path to enhanced face |
| `upscale_image` | image_path, scale_factor? (2x/4x) | path to upscaled PNG |

**Approach:**
- `photo_to_headshot`: GPT-image edit with prompt "professional corporate headshot".
- `photo_to_cartoon`: GPT-image with style prompt.
- `photo_to_vector`: Pillow trace (potrace-like) or GPT-image → SVG conversion.
- `upscale_image`: `pillow-simd` or `realesrgan` if available, fallback to Pillow LANCZOS.
- `style_transfer`: GPT-image with style reference, or neural-style-transfer if torch available.
- `face_enhancement`: GFPGAN / CodeFormer if available, GPT-image fallback.

**Verify:** Before/after comparisons. Check dimensions increase for upscale. Check style transfer retains content.

---

## Dependencies

```toml
[project]
requires-python = ">=3.14"
dependencies = [
    "mcp[cli]>=1.0",        # FastMCP
    "pillow>=11.0",          # core image ops
    "rembg[gpu]>=2.0",      # AI background removal
    "openai>=1.50",          # GPT-4o vision + GPT-image
    "Pillow[webp]>=11.0",   # WebP support
    "pydantic>=2.0",         # tool parameter validation
    "pymupdf>=1.24",         # PDF reading
    "reportlab>=4.0",        # PDF writing
    "cairosvg>=2.7",         # SVG rasterization
    "pytesseract>=0.3",      # OCR (for erase_text)
    "numpy>=2.0",            # array ops for masks
]
```

Optional (install separately if GPU available):
```
real-esrgan   # for upscale_image
gfpgan        # for face_enhancement
onnxruntime   # faster rembg inference
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Required for AI tools (generation, analysis, inpainting, vision) |
| `IMAGEMCP_STORAGE` | Optional: base path for temp files (default: system temp) |

---

## How an LLM Uses This

```
User: "Crop this screenshot to the nav bar and extract the color palette"

LLM calls:
1. screenshot_to_component_tree(image="/tmp/shot.png")
   → returns { "nav": { "bounds": [0, 0, 1200, 60], ... } }
2. crop_image(image="/tmp/shot.png", x=0, y=0, width=1200, height=60)
   → returns "/tmp/cropped_nav.png"
3. extract_colors(image="/tmp/cropped_nav.png")
   → returns [{"hex": "#1a1a2e", "pct": 45}, {"hex": "#e94560", "pct": 30}, ...]
```

---

## Implementation Notes

1. **File I/O pattern:** All tools accept file paths, return file paths. Temporary files use `IMAGEMCP_STORAGE` or system temp. Never pass raw image data in MCP messages (too large).

2. **AI tool fallbacks:** Every AI tool has a local Pillow fallback (lower quality but works without API key). This makes the server usable offline for basic workflows.

3. **Error handling:** Each tool wraps operations in try/except, returns a clear error message as text (not an exception stack trace). MCP tools should always return a string result.

4. **Image format:** Internal = PNG (lossless, alpha support). Conversions happen at export/input boundaries only.

5. **Canvas state:** The `Canvas` class is stored in a module-level dict keyed by `document_id`. For production, this should be backed by disk or Redis. For now, in-memory is fine.

---

## Phase Execution Order

```
Phase 1 (infra) → Phase 2 (core) → Phase 3 (layers) → Phase 4 (conversions)
                                                                    ↓
                                               Phase 5 (AI seg) ← Phase 4
                                                      ↓
                                               Phase 6 (AI cleanup)
                                                      ↓
                                               Phase 7 (AI generation)
                                                      ↓
                                               Phase 8 (design analysis)
                                                      ↓
                                               Phase 9 (screenshot→code)
                                                      ↓
                                               Phase 10 (smart export)
                                                      ↓
                                               Phase 11 (advanced AI)
```

Phases 2-4 can be parallelized after Phase 1. Phases 5-11 are sequential (each builds on prior infrastructure).

---

## Success Criteria

- [ ] `mcp list_tools` shows all ~55 tools
- [ ] Every core editing tool has passing unit tests
- [ ] AI tools work with valid ANTHROPIC_API_KEY
- [ ] AI tools degrade gracefully without API key (local fallback)
- [ ] Layer operations correctly composite
- [ ] Conversions preserve dimensions and quality
- [ ] Screenshot-to-code produces syntactically valid output
- [ ] Exports produce valid files (PNG renders, SVG is valid, React/Tailwind is parseable)
