"""
Hand-Drawn Editorial Scientific Illustrations Engine
====================================================
Procedurally renders minimal, scientific, hand-crafted ink line-art
illustrations for research papers and editorial publication headers.

Uses aspect-ratio corrected vector primitives so circles and geometry
remain geometrically proportional on tall portrait canvases.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import (
    Ellipse,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)

from src.infographic.palette import (
    ACCENT_MAUVE,
    ACCENT_OCHRE,
    ACCENT_SAGE,
    ACCENT_TERRACOTTA,
    INK_MUTED,
    INK_PRIMARY,
    PAPER_BG,
    get_wash_for_accent,
)

# Canvas aspect ratio width / height (10.0 / 14.14)
AR = 10.0 / 14.14  # ~0.7072


def draw_book_stack_header(ax: plt.Axes, x: float, y: float, scale: float = 0.30) -> None:
    """
    Renders an editorial stack of 4 research volumes with titled spines
    and a delicate botanical sprig.
    Spines: RESEARCH, ANALYZE, LEARN, BUILD.
    """
    titles = ["BUILD", "LEARN", "ANALYZE", "RESEARCH"]
    spine_colors = [ACCENT_SAGE, ACCENT_TERRACOTTA, INK_PRIMARY, ACCENT_OCHRE]
    wash_colors = [
        get_wash_for_accent(c) if c != INK_PRIMARY else "#E2DCD4"
        for c in spine_colors
    ]

    base_w = 0.46 * scale
    book_h = 0.065 * scale * AR
    start_y = y

    # Drop shadow
    shadow = Ellipse(
        (x + base_w * 0.48, start_y - 0.005),
        base_w * 1.05, 0.025 * scale * AR,
        facecolor="#D6CEBE", edgecolor="none", alpha=0.5
    )
    ax.add_patch(shadow)

    for i, (title, color, wash) in enumerate(zip(titles, spine_colors, wash_colors)):
        book_y = start_y + (i * (book_h * 1.15))
        offset_x = (i % 2) * 0.012 * scale

        # Main spine
        rect = FancyBboxPatch(
            (x + offset_x, book_y), base_w, book_h,
            boxstyle="round,pad=0.002,rounding_size=0.008",
            facecolor=wash,
            edgecolor=INK_PRIMARY,
            linewidth=1.3
        )
        ax.add_patch(rect)

        # Accent end band
        band = Rectangle(
            (x + offset_x + 0.018 * scale, book_y + 0.003 * scale * AR),
            0.018 * scale, book_h - 0.006 * scale * AR,
            facecolor=color, edgecolor=INK_PRIMARY, linewidth=0.7
        )
        ax.add_patch(band)

        # Spine Title Text
        ax.text(
            x + offset_x + base_w * 0.52, book_y + book_h * 0.45,
            title,
            color=INK_PRIMARY,
            fontsize=6.5 * scale * 2.8,
            fontweight="bold",
            ha="center", va="center",
            fontfamily="sans-serif"
        )

        # Page lines
        ax.plot(
            [x + offset_x + base_w * 0.94, x + offset_x + base_w * 0.94],
            [book_y + 0.008 * scale * AR, book_y + book_h - 0.008 * scale * AR],
            color=INK_MUTED, linewidth=0.7
        )

    # Botanical sprig resting on the top book
    sprig_x = x + base_w * 0.65
    sprig_y = start_y + (4 * book_h) + 0.005
    draw_botanical_sprig(ax, sprig_x, sprig_y, scale=scale * 0.65, angle=35)


def draw_botanical_sprig(
    ax: plt.Axes,
    x: float,
    y: float,
    scale: float = 1.0,
    angle: float = 0.0
) -> None:
    """Renders a delicate botanical olive branch / sprig with ink leaves."""
    stem_len = 0.16 * scale
    t = np.linspace(0, stem_len, 20)
    stem_x = x + t * np.cos(np.radians(angle))
    stem_y = y + (t * np.sin(np.radians(angle)) + 0.02 * np.sin(t / stem_len * np.pi)) * AR
    ax.plot(stem_x, stem_y, color=INK_PRIMARY, linewidth=1.1)

    leaf_locs = [0.25, 0.55, 0.85, 1.0]
    for loc in leaf_locs:
        idx = int(loc * (len(t) - 1))
        lx = stem_x[idx]
        ly = stem_y[idx]

        leaf_l = Ellipse(
            (lx - 0.016 * scale, ly + 0.015 * scale * AR),
            0.035 * scale, 0.018 * scale * AR,
            angle=angle + 35,
            facecolor="#E2EADF",
            edgecolor=INK_PRIMARY,
            linewidth=0.9
        )
        ax.add_patch(leaf_l)

        leaf_r = Ellipse(
            (lx + 0.016 * scale, ly - 0.010 * scale * AR),
            0.035 * scale, 0.016 * scale * AR,
            angle=angle - 30,
            facecolor="#E2EADF",
            edgecolor=INK_PRIMARY,
            linewidth=0.9
        )
        ax.add_patch(leaf_r)


def draw_quadruped_robot(
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_TERRACOTTA
) -> None:
    """
    Renders an editorial scientific illustration of an articulated quadruped robot
    with a warm terracotta sun halo, mechanical joints, and ground hatching.
    """
    sun_r = 0.18 * scale
    halo_cy = cy + 0.02 * scale * AR
    halo_cx = cx + 0.02 * scale

    # Terracotta Sun Halo (Aspect-ratio corrected)
    halo = Ellipse(
        (halo_cx, halo_cy),
        2 * sun_r, 2 * sun_r * AR,
        facecolor=get_wash_for_accent(accent),
        edgecolor=accent,
        linewidth=1.0,
        alpha=0.75
    )
    ax.add_patch(halo)

    # Delicate sun ink hatch texture
    for hy in np.linspace(-sun_r * 0.65, sun_r * 0.65, 5):
        hw = np.sqrt(max(0, sun_r**2 - hy**2)) * 0.70
        ax.plot(
            [halo_cx - hw, halo_cx + hw],
            [halo_cy + hy * AR, halo_cy + hy * AR],
            color=accent, linewidth=0.7, alpha=0.45
        )

    # Ground Hatching Shadow
    gx_start = cx - 0.22 * scale
    gx_end = cx + 0.24 * scale
    gy = cy - 0.135 * scale * AR
    ax.plot([gx_start, gx_end], [gy, gy], color=INK_PRIMARY, linewidth=1.2)
    for hx in np.linspace(gx_start + 0.03 * scale, gx_end - 0.03 * scale, 7):
        ax.plot([hx, hx + 0.016 * scale], [gy, gy - 0.014 * scale * AR], color=INK_MUTED, linewidth=0.8)

    # Background Legs (rendered behind chassis)
    hip_rl = (cx - 0.06 * scale, cy + 0.005 * scale * AR)
    knee_rl = (cx - 0.11 * scale, cy - 0.06 * scale * AR)
    foot_rl = (cx - 0.13 * scale, gy)
    _draw_robot_leg(ax, hip_rl, knee_rl, foot_rl, scale, is_front=False)

    hip_fl = (cx + 0.06 * scale, cy + 0.01 * scale * AR)
    knee_fl = (cx + 0.09 * scale, cy - 0.06 * scale * AR)
    foot_fl = (cx + 0.10 * scale, gy)
    _draw_robot_leg(ax, hip_fl, knee_fl, foot_fl, scale, is_front=False)

    # Robot Main Body Chassis
    body_poly = np.array([
        [cx - 0.11 * scale, cy + 0.04 * scale * AR],
        [cx + 0.08 * scale, cy + 0.045 * scale * AR],
        [cx + 0.11 * scale, cy - 0.01 * scale * AR],
        [cx + 0.07 * scale, cy - 0.035 * scale * AR],
        [cx - 0.09 * scale, cy - 0.035 * scale * AR],
        [cx - 0.12 * scale, cy - 0.005 * scale * AR],
    ])
    body_patch = Polygon(
        body_poly, closed=True,
        facecolor=PAPER_BG, edgecolor=INK_PRIMARY, linewidth=1.5
    )
    ax.add_patch(body_patch)

    # Top Battery/Payload Module
    top_pack = FancyBboxPatch(
        (cx - 0.06 * scale, cy + 0.042 * scale * AR),
        0.10 * scale, 0.022 * scale * AR,
        boxstyle="round,pad=0.002,rounding_size=0.005",
        facecolor=get_wash_for_accent(accent), edgecolor=INK_PRIMARY, linewidth=1.1
    )
    ax.add_patch(top_pack)

    # Chassis Panel Ribs
    ax.plot(
        [cx - 0.02 * scale, cx - 0.02 * scale],
        [cy - 0.025 * scale * AR, cy + 0.035 * scale * AR],
        color=INK_MUTED, linewidth=0.9
    )
    ax.plot(
        [cx + 0.03 * scale, cx + 0.03 * scale],
        [cy - 0.025 * scale * AR, cy + 0.035 * scale * AR],
        color=INK_MUTED, linewidth=0.9
    )

    # Sensor Head Assembly (Forward looking LiDAR / vision head)
    head_poly = np.array([
        [cx + 0.10 * scale, cy + 0.025 * scale * AR],
        [cx + 0.16 * scale, cy + 0.03 * scale * AR],
        [cx + 0.18 * scale, cy - 0.01 * scale * AR],
        [cx + 0.11 * scale, cy - 0.02 * scale * AR],
    ])
    head_patch = Polygon(
        head_poly, closed=True,
        facecolor="#E8E2D5", edgecolor=INK_PRIMARY, linewidth=1.3
    )
    ax.add_patch(head_patch)

    # Camera / Vision Eye Lens
    eye = Ellipse(
        (cx + 0.15 * scale, cy + 0.01 * scale * AR),
        0.020 * scale, 0.020 * scale * AR,
        facecolor=INK_PRIMARY, edgecolor=INK_PRIMARY
    )
    ax.add_patch(eye)

    # Foreground Legs (rendered in front of chassis)
    hip_rr = (cx - 0.08 * scale, cy - 0.01 * scale * AR)
    knee_rr = (cx - 0.15 * scale, cy - 0.065 * scale * AR)
    foot_rr = (cx - 0.18 * scale, gy)
    _draw_robot_leg(ax, hip_rr, knee_rr, foot_rr, scale, is_front=True)

    hip_fr = (cx + 0.07 * scale, cy - 0.01 * scale * AR)
    knee_fr = (cx + 0.14 * scale, cy - 0.065 * scale * AR)
    foot_fr = (cx + 0.17 * scale, gy)
    _draw_robot_leg(ax, hip_fr, knee_fr, foot_fr, scale, is_front=True)


def _draw_robot_leg(
    ax: plt.Axes,
    hip: tuple,
    knee: tuple,
    foot: tuple,
    scale: float,
    is_front: bool = True
) -> None:
    color = INK_PRIMARY if is_front else "#76716B"
    lw = 1.5 if is_front else 1.1

    ax.plot([hip[0], knee[0]], [hip[1], knee[1]], color=color, linewidth=lw)
    ax.plot([knee[0], foot[0]], [knee[1], foot[1]], color=color, linewidth=lw)

    hip_joint = Ellipse(hip, 0.018 * scale, 0.018 * scale * AR, facecolor=PAPER_BG, edgecolor=color, linewidth=1.1)
    ax.add_patch(hip_joint)

    knee_joint = Ellipse(knee, 0.016 * scale, 0.016 * scale * AR, facecolor=PAPER_BG, edgecolor=color, linewidth=1.1)
    ax.add_patch(knee_joint)

    foot_pad = Rectangle(
        (foot[0] - 0.012 * scale, foot[1] - 0.005 * scale * AR),
        0.024 * scale, 0.008 * scale * AR,
        facecolor=color, edgecolor="none"
    )
    ax.add_patch(foot_pad)


def draw_edge_chip(
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_SAGE
) -> None:
    """
    Renders an editorial scientific illustration of an embedded microprocessor
    chip with pins, 'AI' die marking, and circuit traces transitioning into botanical sprigs.
    """
    chip_wash = Ellipse(
        (cx, cy), 0.36 * scale, 0.36 * scale * AR,
        facecolor=get_wash_for_accent(accent), edgecolor=accent,
        linewidth=1.0, alpha=0.70
    )
    ax.add_patch(chip_wash)

    # Outer Ceramic Package
    pkg_w = 0.18 * scale
    pkg_h = pkg_w * AR
    pkg_rect = FancyBboxPatch(
        (cx - pkg_w / 2, cy - pkg_h / 2),
        pkg_w, pkg_h,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor=PAPER_BG, edgecolor=INK_PRIMARY, linewidth=1.5
    )
    ax.add_patch(pkg_rect)

    # Central Die Square
    die_w = 0.11 * scale
    die_h = die_w * AR
    die_rect = Rectangle(
        (cx - die_w / 2, cy - die_h / 2),
        die_w, die_h,
        facecolor=get_wash_for_accent(accent), edgecolor=INK_PRIMARY, linewidth=1.1
    )
    ax.add_patch(die_rect)

    # 'AI' Monogram
    ax.text(
        cx, cy, "AI",
        color=INK_PRIMARY,
        fontsize=14 * scale,
        fontweight="bold",
        fontfamily="serif",
        ha="center", va="center"
    )

    # Pins
    pin_len_x = 0.03 * scale
    pin_len_y = pin_len_x * AR
    num_pins = 4
    pin_step_x = pkg_w / (num_pins + 1)
    pin_step_y = pkg_h / (num_pins + 1)

    for i in range(1, num_pins + 1):
        pos_x = -pkg_w / 2 + (i * pin_step_x)
        pos_y = -pkg_h / 2 + (i * pin_step_y)

        # Top / Bottom
        ax.plot([cx + pos_x, cx + pos_x], [cy + pkg_h / 2, cy + pkg_h / 2 + pin_len_y], color=INK_PRIMARY, linewidth=1.3)
        ax.plot([cx + pos_x, cx + pos_x], [cy - pkg_h / 2, cy - pkg_h / 2 - pin_len_y], color=INK_PRIMARY, linewidth=1.3)
        # Left / Right
        ax.plot([cx + pkg_w / 2, cx + pkg_w / 2 + pin_len_x], [cy + pos_y, cy + pos_y], color=INK_PRIMARY, linewidth=1.3)
        ax.plot([cx - pkg_w / 2, cx - pkg_w / 2 - pin_len_x], [cy + pos_y, cy + pos_y], color=INK_PRIMARY, linewidth=1.3)

    # Delicate leaf sprouting from corner
    draw_botanical_sprig(ax, cx + 0.10 * scale, cy + 0.07 * scale * AR, scale=scale * 0.65, angle=50)


def draw_warehouse_agv(
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_MAUVE
) -> None:
    """
    Renders an editorial scientific illustration of autonomous warehouse vehicles (AGVs)
    and modular shelving racks coordinating transport tasks.
    """
    wh_wash = Ellipse(
        (cx, cy), 0.38 * scale, 0.38 * scale * AR,
        facecolor=get_wash_for_accent(accent), edgecolor=accent,
        linewidth=1.0, alpha=0.70
    )
    ax.add_patch(wh_wash)

    # Shelving Rack in Background
    rack_x = cx - 0.15 * scale
    rack_y = cy - 0.06 * scale * AR
    rack_w = 0.12 * scale
    rack_h = 0.20 * scale * AR

    # Uprights
    ax.plot([rack_x, rack_x], [rack_y, rack_y + rack_h], color=INK_PRIMARY, linewidth=1.2)
    ax.plot([rack_x + rack_w, rack_x + rack_w], [rack_y, rack_y + rack_h], color=INK_PRIMARY, linewidth=1.2)

    # Shelves
    for sy in [rack_y + 0.07 * scale * AR, rack_y + 0.14 * scale * AR, rack_y + 0.20 * scale * AR]:
        ax.plot([rack_x, rack_x + rack_w], [sy, sy], color=INK_PRIMARY, linewidth=1.2)
        box = Rectangle(
            (rack_x + 0.018 * scale, sy - 0.045 * scale * AR),
            0.045 * scale, 0.040 * scale * AR,
            facecolor="#EADAB8", edgecolor=INK_PRIMARY, linewidth=0.9
        )
        ax.add_patch(box)

    # AGV Cart 1 (Foreground Left)
    _draw_agv_unit(ax, cx - 0.07 * scale, cy - 0.09 * scale * AR, scale, has_box=True)

    # AGV Cart 2 (Midground Right)
    _draw_agv_unit(ax, cx + 0.08 * scale, cy - 0.03 * scale * AR, scale * 0.82, has_box=True)

    # Communication signal waves
    ax.plot(
        [cx - 0.01 * scale, cx + 0.04 * scale],
        [cy - 0.05 * scale * AR, cy - 0.02 * scale * AR],
        color=accent, linestyle=":", linewidth=1.3
    )


def _draw_agv_unit(
    ax: plt.Axes,
    x: float,
    y: float,
    scale: float,
    has_box: bool = True
) -> None:
    cart_w = 0.095 * scale
    cart_h = 0.028 * scale * AR

    chassis = FancyBboxPatch(
        (x, y), cart_w, cart_h,
        boxstyle="round,pad=0.003,rounding_size=0.008",
        facecolor=PAPER_BG, edgecolor=INK_PRIMARY, linewidth=1.3
    )
    ax.add_patch(chassis)

    # Wheels
    w1 = Ellipse((x + 0.018 * scale, y - 0.007 * scale * AR), 0.016 * scale, 0.016 * scale * AR, facecolor=INK_PRIMARY)
    w2 = Ellipse((x + cart_w - 0.018 * scale, y - 0.007 * scale * AR), 0.016 * scale, 0.016 * scale * AR, facecolor=INK_PRIMARY)
    ax.add_patch(w1)
    ax.add_patch(w2)

    if has_box:
        box_w = 0.065 * scale
        box_h = 0.055 * scale * AR
        box = Rectangle(
            (x + (cart_w - box_w) / 2, y + cart_h),
            box_w, box_h,
            facecolor="#EADAB8", edgecolor=INK_PRIMARY, linewidth=1.1
        )
        ax.add_patch(box)
        ax.plot(
            [x + cart_w / 2, x + cart_w / 2],
            [y + cart_h, y + cart_h + box_h],
            color=INK_PRIMARY, linewidth=0.7
        )


def draw_vision_camera(
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_OCHRE
) -> None:
    """Editorial scientific illustration of a camera aperture / 3D sensor."""
    wash = Ellipse(
        (cx, cy), 0.36 * scale, 0.36 * scale * AR,
        facecolor=get_wash_for_accent(accent), edgecolor=accent,
        linewidth=1.0, alpha=0.70
    )
    ax.add_patch(wash)

    r1 = Ellipse((cx, cy), 0.22 * scale, 0.22 * scale * AR, facecolor=PAPER_BG, edgecolor=INK_PRIMARY, linewidth=1.4)
    r2 = Ellipse((cx, cy), 0.15 * scale, 0.15 * scale * AR, facecolor="none", edgecolor=INK_PRIMARY, linewidth=1.0)
    r3 = Ellipse((cx, cy), 0.08 * scale, 0.08 * scale * AR, facecolor=get_wash_for_accent(accent), edgecolor=INK_PRIMARY, linewidth=1.1)
    center = Ellipse((cx, cy), 0.03 * scale, 0.03 * scale * AR, facecolor=INK_PRIMARY, edgecolor=INK_PRIMARY)

    for patch in [r1, r2, r3, center]:
        ax.add_patch(patch)


def draw_knowledge_graph(
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_MAUVE
) -> None:
    """Editorial scientific illustration of a semantic knowledge graph."""
    wash = Ellipse(
        (cx, cy), 0.36 * scale, 0.36 * scale * AR,
        facecolor=get_wash_for_accent(accent), edgecolor=accent,
        linewidth=1.0, alpha=0.70
    )
    ax.add_patch(wash)

    nodes = [
        (cx - 0.07 * scale, cy + 0.07 * scale * AR),
        (cx + 0.06 * scale, cy + 0.08 * scale * AR),
        (cx, cy),
        (cx - 0.08 * scale, cy - 0.06 * scale * AR),
        (cx + 0.07 * scale, cy - 0.07 * scale * AR),
    ]

    edges = [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]
    for n1, n2 in edges:
        p1 = nodes[n1]
        p2 = nodes[n2]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INK_PRIMARY, linewidth=1.2)

    for i, (nx, ny) in enumerate(nodes):
        r = 0.035 * scale if i == 2 else 0.026 * scale
        c = Ellipse(
            (nx, ny), r, r * AR,
            facecolor=PAPER_BG, edgecolor=INK_PRIMARY, linewidth=1.3
        )
        ax.add_patch(c)


def render_paper_illustration(
    paper_title: str,
    abstract: str,
    category: str,
    ax: plt.Axes,
    cx: float,
    cy: float,
    scale: float = 1.0,
    accent: str = ACCENT_TERRACOTTA
) -> None:
    """
    Carefully prioritized concept dispatcher ensuring specific themes
    (e.g., warehouse multi-agent, microcontrollers) take precedence over generic keywords.
    """
    combined = f"{paper_title} {abstract} {category}".lower()

    # 1. Robotics Legged Locomotion & Quadruped (Specific physical embodiment)
    if any(k in combined for k in ["quadruped", "locomotion", "legged", "bipedal", "robot dog", "st-locovit"]):
        draw_quadruped_robot(ax, cx, cy, scale=scale, accent=accent)
    # 2. Multi-Agent & Warehouse Logistics
    elif any(k in combined for k in ["multi-agent", "warehouse", "swarm", "fleet", "task allocation", "deadlock", "agv"]):
        draw_warehouse_agv(ax, cx, cy, scale=scale, accent=accent)
    # 3. Edge Computing, Embedded & Quantization
    elif any(k in combined for k in ["edge", "quantiz", "tinyml", "milliwatt", "microcontroller", "low-power", "sub-milliwatt", "microquant", "cs.dc"]):
        draw_edge_chip(ax, cx, cy, scale=scale, accent=accent)
    # 4. General Robotics & Manipulation
    elif any(k in combined for k in ["robot", "manipulat", "cs.ro"]):
        draw_quadruped_robot(ax, cx, cy, scale=scale, accent=accent)
    # 5. Computer Vision & 3D Sensing
    elif any(k in combined for k in ["vision", "camera", "nerf", "gaussian", "image", "3d", "cs.cv"]):
        draw_vision_camera(ax, cx, cy, scale=scale, accent=accent)
    # 6. Language Models & Reasoning Networks
    else:
        draw_knowledge_graph(ax, cx, cy, scale=scale, accent=accent)
