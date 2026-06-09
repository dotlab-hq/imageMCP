"""In-memory layer canvas for compositing."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Layer:
    id: str
    name: str
    image: Image.Image
    x: int = 0
    y: int = 0

    @property
    def width(self) -> int:
        return self.image.width

    @property
    def height(self) -> int:
        return self.image.height

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }


class Canvas:
    def __init__(self, width: int, height: int, bg_color: str = "#ffffff"):
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.layers: list[Layer] = []

    def add_layer(self, image: Image.Image, x: int = 0, y: int = 0, name: str = "") -> Layer:
        lid = uuid.uuid4().hex[:8]
        layer = Layer(id=lid, name=name or f"layer_{len(self.layers)}", image=image.copy(), x=x, y=y)
        self.layers.append(layer)
        return layer

    def add_text_layer(self, text: str, x: int, y: int, font_size: int = 24, color: str = "#000000", name: str = "") -> Layer:
        font = ImageFont.truetype("arial.ttf", font_size) if _font_exists("arial") else ImageFont.load_default()
        bbox = font.getbbox(text)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        img = Image.new("RGBA", (w + 10, h + 10), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), text, fill=color, font=font)
        return self.add_layer(img, x, y, name)

    def move_layer(self, layer_id: str, x: int, y: int) -> Layer:
        layer = self.get_layer(layer_id)
        layer.x, layer.y = x, y
        return layer

    def resize_layer(self, layer_id: str, width: int, height: int) -> Layer:
        layer = self.get_layer(layer_id)
        layer.image = layer.image.resize((width, height), Image.LANCZOS)
        return layer

    def delete_layer(self, layer_id: str) -> None:
        self.layers = [l for l in self.layers if l.id != layer_id]

    def duplicate_layer(self, layer_id: str) -> Layer:
        src = self.get_layer(layer_id)
        return self.add_layer(src.image.copy(), src.x, src.y, f"{src.name}_copy")

    def get_layer(self, layer_id: str) -> Layer:
        for l in self.layers:
            if l.id == layer_id:
                return l
        raise ValueError(f"Layer {layer_id} not found")

    def flatten(self) -> Image.Image:
        canvas = Image.new("RGBA", (self.width, self.height), self.bg_color)
        for layer in self.layers:
            canvas.paste(layer.image, (layer.x, layer.y), layer.image)
        return canvas

    def list_layers(self) -> list[dict]:
        return [l.to_dict() for l in self.layers]


def _font_exists(name: str) -> bool:
    try:
        ImageFont.truetype(f"{name}.ttf", 12)
        return True
    except (OSError, IOError):
        return False


# Global canvas store — keyed by document_id
_canvas_store: dict[str, Canvas] = {}


def get_canvas(doc_id: str) -> Canvas:
    if doc_id not in _canvas_store:
        raise ValueError(f"Document {doc_id} not found")
    return _canvas_store[doc_id]


def put_canvas(canvas: Canvas) -> str:
    import uuid
    doc_id = uuid.uuid4().hex[:8]
    _canvas_store[doc_id] = canvas
    return doc_id


def remove_canvas(doc_id: str) -> None:
    _canvas_store.pop(doc_id, None)
