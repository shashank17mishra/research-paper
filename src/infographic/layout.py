"""
Editorial Layout Geometry and Grid Engine
=========================================
Computes exact bounding boxes, column splits, and vertical coordinates
for the portrait magazine layout (A4 aspect ratio: ~2480 x 3508 px at 300 DPI).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass
class PaperRowLayout:
    """Bounding box coordinates for a single featured research row."""
    y_bottom: float
    y_top: float
    height: float
    # X column ranges
    col_rank: Tuple[float, float]       # Large number & score
    col_content: Tuple[float, float]    # Title, authors, What/How explanation
    col_illus: Tuple[float, float]      # Vector line-art scientific illustration
    col_concepts: Tuple[float, float]   # Key concepts & Why it matters


@dataclass
class EditorialLayout:
    """Master layout geometry containing coordinates for all page sections."""
    # Global canvas bounds
    margin_x: float = 0.045
    margin_y: float = 0.025

    # Header section
    header_y_bottom: float = 0.835
    header_y_top: float = 0.975

    # Featured research section
    featured_header_y: float = 0.805
    row_1: PaperRowLayout = None
    row_2: PaperRowLayout = None
    row_3: PaperRowLayout = None

    # Bottom overview section (3 columns)
    bottom_y_bottom: float = 0.045
    bottom_y_top: float = 0.190
    col_areas: Tuple[float, float] = None
    col_concepts_grid: Tuple[float, float] = None
    col_insight: Tuple[float, float] = None

    # Footer section
    footer_y: float = 0.015


def compute_editorial_layout() -> EditorialLayout:
    """Calculates all layout dimensions and returns configured EditorialLayout."""
    mx = 0.045
    right_edge = 1.0 - mx

    # 3 featured paper rows in middle 60% of page
    row_h = 0.190
    spacing = 0.005

    row_1_top = 0.795
    row_1_bottom = row_1_top - row_h

    row_2_top = row_1_bottom - spacing
    row_2_bottom = row_2_top - row_h

    row_3_top = row_2_bottom - spacing
    row_3_bottom = row_3_top - row_h

    # Horizontal split for paper rows:
    # 0.045 - 0.160: Rank (01), Score, Category Badge
    # 0.170 - 0.490: Title, Authors, Plain Language Summary
    # 0.505 - 0.760: Scientific Illustration
    # 0.780 - 0.955: Key Concepts + Why It Matters
    col_rank = (mx, 0.160)
    col_content = (0.175, 0.495)
    col_illus = (0.510, 0.765)
    col_concepts = (0.785, right_edge)

    r1 = PaperRowLayout(
        y_bottom=row_1_bottom, y_top=row_1_top, height=row_h,
        col_rank=col_rank, col_content=col_content,
        col_illus=col_illus, col_concepts=col_concepts
    )
    r2 = PaperRowLayout(
        y_bottom=row_2_bottom, y_top=row_2_top, height=row_h,
        col_rank=col_rank, col_content=col_content,
        col_illus=col_illus, col_concepts=col_concepts
    )
    r3 = PaperRowLayout(
        y_bottom=row_3_bottom, y_top=row_3_top, height=row_h,
        col_rank=col_rank, col_content=col_content,
        col_illus=col_illus, col_concepts=col_concepts
    )

    # Bottom 3-column split
    col_w = (right_edge - mx - 0.04) / 3
    c1 = (mx, mx + col_w)
    c2 = (mx + col_w + 0.02, mx + 2 * col_w + 0.02)
    c3 = (mx + 2 * col_w + 0.04, right_edge)

    return EditorialLayout(
        margin_x=mx,
        margin_y=0.020,
        header_y_bottom=0.835,
        header_y_top=0.975,
        featured_header_y=0.810,
        row_1=r1,
        row_2=r2,
        row_3=r3,
        bottom_y_bottom=0.048,
        bottom_y_top=0.195,
        col_areas=c1,
        col_concepts_grid=c2,
        col_insight=c3,
        footer_y=0.016
    )
