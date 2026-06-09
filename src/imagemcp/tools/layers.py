"""Layer management tools — document model for compositing."""

from PIL import Image
from imagemcp.utils.canvas import Canvas, get_canvas, put_canvas
from imagemcp.utils.io import load_image


def create_document(width: int, height: int, background_color: str = "#ffffff") -> str:
    """Create a new blank document (canvas) with the given dimensions and background color."""
    canvas = Canvas(width, height, background_color)
    return put_canvas(canvas)


def add_image_layer(document_id: str, image_path: str, x: int = 0, y: int = 0, name: str = "") -> str:
    """Add an image as a new layer to the document at the specified position."""
    canvas = get_canvas(document_id)
    img = load_image(image_path)
    layer = canvas.add_layer(img, x, y, name)
    return layer.id


def add_text_layer(document_id: str, text: str, x: int, y: int, font_size: int = 24, color: str = "#000000", name: str = "") -> str:
    """Add a text layer to the document at the specified position."""
    canvas = get_canvas(document_id)
    layer = canvas.add_text_layer(text, x, y, font_size, color, name)
    return layer.id


def move_layer(document_id: str, layer_id: str, x: int, y: int) -> str:
    """Move a layer to the specified position in the document."""
    canvas = get_canvas(document_id)
    canvas.move_layer(layer_id, x, y)
    return f"Layer {layer_id} moved to ({x}, {y})"


def resize_layer(document_id: str, layer_id: str, width: int, height: int) -> str:
    """Resize a layer to the specified width and height."""
    canvas = get_canvas(document_id)
    canvas.resize_layer(layer_id, width, height)
    return f"Layer {layer_id} resized to ({width}x{height})"


def delete_layer(document_id: str, layer_id: str) -> str:
    """Delete a layer from the document."""
    canvas = get_canvas(document_id)
    canvas.delete_layer(layer_id)
    return f"Layer {layer_id} deleted"


def duplicate_layer(document_id: str, layer_id: str) -> str:
    """Duplicate a layer and return the ID of the new copy."""
    canvas = get_canvas(document_id)
    dup = canvas.duplicate_layer(layer_id)
    return dup.id


def list_layers(document_id: str) -> list[dict]:
    """List all layers in the document with their properties."""
    canvas = get_canvas(document_id)
    return canvas.list_layers()


def export_canvas(document_id: str) -> str:
    from imagemcp.utils.io import save_image
    canvas = get_canvas(document_id)
    return save_image(canvas.flatten())
