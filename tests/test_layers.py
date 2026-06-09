"""Tests for layer management tools."""

import os
import pytest
from PIL import Image

from imagemcp.tools.layers import (
    create_document,
    add_image_layer,
    add_text_layer,
    move_layer,
    resize_layer,
    delete_layer,
    duplicate_layer,
    list_layers,
    export_canvas,
)


class TestCreateDocument:
    def test_basic(self):
        doc_id = create_document(800, 600)
        assert isinstance(doc_id, str)
        assert len(doc_id) == 8

    def test_with_color(self):
        doc_id = create_document(400, 300, background_color="#ff0000")
        assert len(doc_id) == 8

    def test_layers_empty(self):
        doc_id = create_document(800, 600)
        layers = list_layers(doc_id)
        assert layers == []


class TestAddImageLayer:
    def test_add_one(self, img_path):
        doc_id = create_document(800, 600)
        layer_id = add_image_layer(doc_id, img_path)
        assert isinstance(layer_id, str)
        layers = list_layers(doc_id)
        assert len(layers) == 1
        assert layers[0]["id"] == layer_id

    def test_add_with_position(self, img_path):
        doc_id = create_document(800, 600)
        layer_id = add_image_layer(doc_id, img_path, x=100, y=50, name="bg")
        layers = list_layers(doc_id)
        assert layers[0]["x"] == 100
        assert layers[0]["y"] == 50
        assert layers[0]["name"] == "bg"

    def test_add_multiple(self, img_path, landscape_path):
        doc_id = create_document(1200, 800)
        l1 = add_image_layer(doc_id, img_path, name="layer1")
        l2 = add_image_layer(doc_id, landscape_path, x=200, name="layer2")
        layers = list_layers(doc_id)
        assert len(layers) == 2
        assert l1 != l2


class TestAddTextLayer:
    def test_basic(self):
        doc_id = create_document(800, 600)
        layer_id = add_text_layer(doc_id, "Hello", x=50, y=50)
        assert isinstance(layer_id, str)
        layers = list_layers(doc_id)
        assert len(layers) == 1

    def test_with_styling(self):
        doc_id = create_document(800, 600)
        layer_id = add_text_layer(doc_id, "Styled", x=10, y=10, font_size=48, color="#ff0000")
        layers = list_layers(doc_id)
        assert layers[0]["name"]


class TestMoveLayer:
    def test_move(self, img_path):
        doc_id = create_document(800, 600)
        lid = add_image_layer(doc_id, img_path, x=0, y=0)
        move_layer(doc_id, lid, x=200, y=100)
        layers = list_layers(doc_id)
        assert layers[0]["x"] == 200
        assert layers[0]["y"] == 100

    def test_move_nonexistent(self, img_path):
        doc_id = create_document(800, 600)
        with pytest.raises(ValueError, match="not found"):
            move_layer(doc_id, "bad_id", x=0, y=0)


class TestResizeLayer:
    def test_resize(self, img_path):
        doc_id = create_document(800, 600)
        lid = add_image_layer(doc_id, img_path)
        resize_layer(doc_id, lid, width=200, height=150)
        layers = list_layers(doc_id)
        assert layers[0]["width"] == 200
        assert layers[0]["height"] == 150


class TestDeleteLayer:
    def test_delete(self, img_path):
        doc_id = create_document(800, 600)
        lid = add_image_layer(doc_id, img_path)
        assert len(list_layers(doc_id)) == 1
        delete_layer(doc_id, lid)
        assert len(list_layers(doc_id)) == 0


class TestDuplicateLayer:
    def test_duplicate(self, img_path):
        doc_id = create_document(800, 600)
        lid = add_image_layer(doc_id, img_path, name="original")
        dup_id = duplicate_layer(doc_id, lid)
        assert dup_id != lid
        layers = list_layers(doc_id)
        assert len(layers) == 2
        assert layers[1]["name"] == "original_copy"


class TestExportCanvas:
    def test_export_empty(self):
        doc_id = create_document(800, 600)
        out = export_canvas(doc_id)
        assert os.path.exists(out)
        img = Image.open(out)
        assert img.size == (800, 600)

    def test_export_with_layers(self, img_path):
        doc_id = create_document(800, 600, background_color="#ffffff")
        add_image_layer(doc_id, img_path, x=0, y=0)
        out = export_canvas(doc_id)
        img = Image.open(out)
        assert img.size == (800, 600)

    def test_export_composite(self, img_path, landscape_path):
        doc_id = create_document(1200, 800)
        add_image_layer(doc_id, img_path, x=0, y=0, name="bg")
        add_text_layer(doc_id, "Overlay", x=100, y=100)
        out = export_canvas(doc_id)
        img = Image.open(out)
        assert img.size == (1200, 800)
