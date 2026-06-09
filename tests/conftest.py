"""Pytest conftest — shared fixtures for all test modules.

Ensures tests/assets/ exists and contains every required file before any test runs.
"""

import subprocess
import sys
from pathlib import Path

import pytest

ASSETS_DIR = Path(__file__).parent / "assets"

REQUIRED = [
    "dog.jpg",
    "landscape.jpg",
    "portrait.jpg",
    "ui_screenshot.png",
    "test.webp",
    "test.svg",
    "test.pdf",
]


def _ensure_assets():
    if all((ASSETS_DIR / f).exists() for f in REQUIRED):
        return
    subprocess.check_call(
        [sys.executable, "-m", "tests.download_assets"],
        cwd=str(Path(__file__).parent.parent),
    )


_ensure_assets()


@pytest.fixture(scope="session")
def assets() -> dict[str, str]:
    """Return a dict mapping logical asset names to absolute file paths."""
    return {name: str(ASSETS_DIR / name) for name in REQUIRED}


@pytest.fixture(scope="session")
def img_path(assets) -> str:
    """Path to the primary test image (800×600 jpg)."""
    return assets["dog.jpg"]


@pytest.fixture(scope="session")
def landscape_path(assets) -> str:
    return assets["landscape.jpg"]


@pytest.fixture(scope="session")
def portrait_path(assets) -> str:
    return assets["portrait.jpg"]


@pytest.fixture(scope="session")
def ui_path(assets) -> str:
    return assets["ui_screenshot.png"]


@pytest.fixture(scope="session")
def webp_path(assets) -> str:
    return assets["test.webp"]


@pytest.fixture(scope="session")
def svg_path(assets) -> str:
    return assets["test.svg"]


@pytest.fixture(scope="session")
def pdf_path(assets) -> str:
    return assets["test.pdf"]
