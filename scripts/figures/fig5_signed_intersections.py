"""Figure 5: Sum of signed intersections.

Two rightward rays from A (inside) and B (outside). Each intersection
is labelled with its sign (+1 / -1). Sum at the ray tip shows the
winding number.

Sign rule: upward crossing (y increases along edge) → +1
           downward crossing                         → -1
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from scene import VERTICES, POINT_A, POINT_B, XLIM, YLIM, FIGSIZE
from utils import (COLORS, setup_ax, save_fig,
                   draw_polygon, draw_labeled_point,
                   add_direction_arrow,
                   ray_signed_intersections_right)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig5_signed_intersections.svg",
))

RAY_X_END = XLIM[1] - 0.1   # rightward ray terminus

SIGN_COLOR = {+1: "#2980B9", -1: "#E74C3C"}   # blue / red

fig, ax = plt.subplots(figsize=FIGSIZE)
fig.patch.set_facecolor(COLORS["background"])
setup_ax(ax)
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

# ── polygon (filled) ─────────────────────────────────────────────────────────
draw_polygon(ax, VERTICES)

# Add two CCW direction arrows on the polygon boundary
xs = np.append(VERTICES[:, 0], VERTICES[0, 0])
ys = np.append(VERTICES[:, 1], VERTICES[0, 1])
add_direction_arrow(ax, xs, ys, frac=0.15, size=18)
add_direction_arrow(ax, xs, ys, frac=0.62, size=18)

# ── rays + signed intersections ───────────────────────────────────────────────
for point, pt_color, pt_label in [
    (POINT_A, COLORS["point_inside"],  "A"),
    (POINT_B, COLORS["point_outside"], "B"),
]:
    px, py = point
    hits = ray_signed_intersections_right(point, VERTICES)

    # Draw the ray
    ax.annotate(
        "",
        xy=(RAY_X_END, py),
        xytext=(px, py),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["ray"],
                        lw=1.5, mutation_scale=14),
        zorder=2,
    )

    # Mark each intersection and label its sign
    wn_sum = 0
    for hx, sign in hits:
        wn_sum += sign
        color = SIGN_COLOR[sign]
        ax.plot(hx, py, "o", color=color, markersize=9, zorder=4,
                markeredgecolor="white", markeredgewidth=0.8)
        label = "+1" if sign == +1 else "−1"
        ax.text(hx, py + 0.22, label,
                fontsize=11, fontweight="bold", ha="center",
                color=color, zorder=5)

    # Sum label at ray end
    sum_str = f"Σ = {wn_sum:+d}"
    ax.text(RAY_X_END + 0.05, py - 0.25, sum_str,
            fontsize=12, fontweight="bold", ha="left",
            color=COLORS["ray"], zorder=5)

# ── query points (drawn last so they sit on top) ──────────────────────────────
draw_labeled_point(ax, POINT_A, "A", COLORS["point_inside"])
draw_labeled_point(ax, POINT_B, "B", COLORS["point_outside"])

save_fig(fig, OUTPUT)
plt.close(fig)
