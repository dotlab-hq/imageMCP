"""Shared Anthropic client and vision/image helpers."""

import base64
import json
import os
from functools import lru_cache
from pathlib import Path

from anthropic import Anthropic


@lru_cache
def get_client() -> Anthropic | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    client = Anthropic(api_key=key)
    # Validate: text-only ping AND image support (1x1 white PNG)
    try:
        resp = client.messages.create(
            model=_DEFAULT_MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        if isinstance(resp, str):
            return None
        # Probe image support with a tiny PNG
        tiny_png = base64.b64encode(
            bytes([
                0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG sig
                0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR
                0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
                0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
                0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT
                0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
                0x00, 0x00, 0x02, 0x00, 0x01, 0xE2, 0x21, 0xBC,
                0x33, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,  # IEND
                0x44, 0xAE, 0x42, 0x60, 0x82,
            ])
        ).decode()
        img_probe = client.messages.create(
            model=_DEFAULT_MODEL,
            max_tokens=1,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": tiny_png}},
                    {"type": "text", "text": "ok"},
                ],
            }],
        )
        if isinstance(img_probe, str):
            return None
        block = img_probe.content[0]
        if isinstance(block, str):
            return None
    except Exception:
        return None
    return client


_DEFAULT_MODEL = "claude-sonnet-4-6"


def image_to_b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def _media_type(path: str) -> str:
    match Path(path).suffix.lower():
        case ".jpg" | ".jpeg": return "image/jpeg"
        case ".webp":           return "image/webp"
        case _:                 return "image/png"


def vision_describe(path: str, prompt: str, model: str = _DEFAULT_MODEL) -> str:
    client = get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    resp = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": _media_type(path), "data": image_to_b64(path)}},
                {"type": "text", "text": prompt},
            ],
        }],
    )
    block = resp.content[0]
    if isinstance(block, str):
        return block
    if hasattr(block, "text"):
        return block.text
    return str(block)


def vision_json(path: str, prompt: str) -> dict:
    raw = vision_describe(
        path,
        f"{prompt}\n\nRespond with ONLY valid JSON. No markdown formatting, no explanation.",
    )
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])
    return json.loads(cleaned)


def generate_image(prompt: str, size: str = "1024x1024", model: str = _DEFAULT_MODEL) -> str:
    from imagemcp.utils.io import _next_path
    client = get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    resp = client.messages.create(
        model=model, max_tokens=4096,
        messages=[{"role": "user", "content": f"Generate an image: {prompt}"}],
    )
    for block in resp.content:
        if hasattr(block, "type") and block.type == "image":
            out = _next_path("png")
            out.write_bytes(base64.b64decode(block.source.data))
            return str(out)
    block = resp.content[0]
    detail = block.text if hasattr(block, "text") else str(block)
    raise RuntimeError(f"Claude did not return an image: {detail}")


def edit_image(image_path: str, mask_path: str | None, prompt: str, model: str = _DEFAULT_MODEL) -> str:
    from imagemcp.utils.io import _next_path
    client = get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    content = [
        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_to_b64(image_path)}},
    ]
    if mask_path:
        content.append({"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image_to_b64(mask_path)}})
        content.append({"type": "text", "text": f"The second image is the edit mask. {prompt}"})
    else:
        content.append({"type": "text", "text": prompt})

    resp = client.messages.create(
        model=model, max_tokens=4096,
        messages=[{"role": "user", "content": content}],
    )
    for block in resp.content:
        if hasattr(block, "type") and block.type == "image":
            out = _next_path("png")
            out.write_bytes(base64.b64decode(block.source.data))
            return str(out)
    block = resp.content[0]
    detail = block.text if hasattr(block, "text") else str(block)
    raise RuntimeError(f"Claude did not return edited image: {detail}")
