"""
Asset Management for Editorial and Modern Infographics
======================================================
Manages loading, caching, and placing raster illustration assets onto
matplotlib canvases with exact aspect-ratio correction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Tuple
import matplotlib.pyplot as plt
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ASSET_DIR = REPO_ROOT / "assets" / "illustrations"

_IMAGE_CACHE: Dict[str, Image.Image] = {}


def get_asset_path(filename: str) -> Path:
    """Returns the absolute path to an illustration asset."""
    return ASSET_DIR / filename


def load_asset(filename: str) -> Optional[Image.Image]:
    """Loads an asset image from disk with memory caching."""
    if filename in _IMAGE_CACHE:
        return _IMAGE_CACHE[filename]
    p = get_asset_path(filename)
    if not p.exists():
        return None
    try:
        im = Image.open(p)
        _IMAGE_CACHE[filename] = im
        return im
    except Exception:
        return None


def place_raster_image(
    ax: plt.Axes,
    filename: str,
    x: float,
    y: float,
    width: float,
    height: Optional[float] = None,
    ha: str = "left",
    va: str = "bottom",
    fig_w: float = 10.0,
    fig_h: float = 14.14,
    zorder: int = 10,
    alpha: float = 1.0,
) -> Optional[Tuple[float, float, float, float]]:
    """
    Places a raster illustration onto the matplotlib axis [0, 1] x [0, 1]
    while strictly preserving the image's original pixel aspect ratio.

    Args:
        ax: Matplotlib axes spanning [0, 1] x [0, 1].
        filename: Name of the asset file in assets/illustrations/.
        x: X-coordinate for anchor point.
        y: Y-coordinate for anchor point.
        width: Bounding width in data coordinates.
        height: Optional fixed height. If None, computed from image aspect ratio.
        ha: Horizontal alignment ('left', 'center', 'right').
        va: Vertical alignment ('bottom', 'center', 'top').
        fig_w: Figure width in inches (default 10.0).
        fig_h: Figure height in inches (default 14.14).
        zorder: Matplotlib zorder layer.
        alpha: Opacity factor (0.0 to 1.0).

    Returns:
        Tuple of (left, right, bottom, top) bounding coordinates, or None.
    """
    im = load_asset(filename)
    if im is None:
        return None

    w_px, h_px = im.size
    aspect_fig = fig_w / fig_h  # e.g., 10.0 / 14.14 ~ 0.7072

    if height is None:
        # Scale height so physical aspect ratio matches image pixel ratio
        h = width * (h_px / w_px) * aspect_fig
    else:
        h = height

    # Horizontal positioning
    if ha == "center":
        left = x - width / 2.0
        right = x + width / 2.0
    elif ha == "right":
        left = x - width
        right = x
    else:  # left
        left = x
        right = x + width

    # Vertical positioning
    if va == "center":
        bottom = y - h / 2.0
        top = y + h / 2.0
    elif va == "top":
        bottom = y - h
        top = y
    else:  # bottom
        bottom = y
        top = y + h

    ax.imshow(
        im,
        extent=[left, right, bottom, top],
        aspect="auto",
        zorder=zorder,
        alpha=alpha,
    )
    return (left, right, bottom, top)
