"""Figure 9: the angular weights of the One-Shot formula.

Duplicate of fig7c's scene (same curve, query point and two sectors) but with
the sample rays removed: instead, two labeled arcs at the query point mark the
angles theta_1 and theta_2 subtended by each sector. These angles, normalized
by 2*pi, are exactly the weights of chi_1 and chi_2 in the One-Shot formula
    w(p) = (theta_1 * chi_1 + theta_2 * chi_2) / (2*pi).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Arc

from utils import COLORS, setup_ax, save_fig
from endpoint_common import (CURVE, P_QUERY, endpoint_dirs, deg_dir, draw_curve,
                             draw_endpoints, draw_query_point)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig9_angle_weights.svg",
))

XLIM = (-2.65, 2.65)
YLIM = (-1.75, 1.75)
WEDGE_R = 6.0

d_lo, d_hi = sorted(endpoint_dirs(P_QUERY))   # ~52deg and ~164deg

fig, ax = plt.subplots(figsize=((XLIM[1] - XLIM[0]) * 0.86, (YLIM[1] - YLIM[0]) * 0.86))
fig.patch.set_facecolor(COLORS["background"])
setup_ax(ax, fill_figure=False)
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

# ── shaded sectors (behind everything): upper = chi_1, lower = chi_2 ─────────
ax.add_patch(Wedge(P_QUERY, WEDGE_R, d_lo, d_hi, facecolor=COLORS["field_pos"],
                   alpha=0.42, edgecolor="none", zorder=0))
ax.add_patch(Wedge(P_QUERY, WEDGE_R, d_hi, d_lo + 360, facecolor=COLORS["field_pos"],
                   alpha=0.18, edgecolor="none", zorder=0))

# ── boundary rays through the endpoints (dashed) ─────────────────────────────
for deg in (d_lo, d_hi):
    ux, uy = deg_dir(deg)
    ax.plot([P_QUERY[0], P_QUERY[0] + ux * WEDGE_R],
            [P_QUERY[1], P_QUERY[1] + uy * WEDGE_R],
            color=COLORS["polygon_edge"], lw=1.4, ls=(0, (4, 3)), zorder=3)

# ── angle arcs at P: each sector's opening angle is the weight of its chi ────
# Drawn in the ray colour (the angles stand in for the swept ray directions);
# theta_2's arc is larger so the two arcs read separately around the same point.
# (radius, angular span, label, label radius) per sector.
for r, a0, a1, label, label_r in [
    (0.40, d_lo, d_hi, r"$\theta_1$", 0.72),
    (0.62, d_hi, d_lo + 360, r"$\theta_2$", 0.98),
]:
    ax.add_patch(Arc(P_QUERY, 2 * r, 2 * r, theta1=a0, theta2=a1,
                     edgecolor=COLORS["ray"], lw=2.5, zorder=6))
    mid = np.deg2rad(0.5 * (a0 + a1))
    ax.text(P_QUERY[0] + label_r * np.cos(mid),
            P_QUERY[1] + label_r * np.sin(mid), label,
            fontsize=15, color=COLORS["ray"],
            ha="center", va="center", zorder=8,
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                      edgecolor="none", alpha=0.85))

# ── curve, endpoints, query point ────────────────────────────────────────────
draw_curve(ax, CURVE, arrow_frac=(0.28, 0.62, 0.9), arrow_size=17, alpha=0.2)
draw_endpoints(ax)
draw_query_point(ax, P_QUERY, dx=-0.12, dy=-0.32)

# ── sector labels (subscripts match the One-Shot formula) ────────────────────
ax.text(-2.4, 1.52, "χ₁ = +2", fontsize=15, fontweight="bold",
        color="#3f8a63", ha="left", va="top", zorder=8)
ax.text(-2.4, -1.52, "χ₂ = +1", fontsize=14, fontweight="bold",
        color="#3f8a63", ha="left", va="bottom", zorder=8)

save_fig(fig, OUTPUT)
if "--png" in sys.argv:   # dev preview
    fig.savefig("/tmp/fig9_preview.png", dpi=150, bbox_inches=None,
                facecolor=COLORS["background"])
    print("Saved: /tmp/fig9_preview.png")
plt.close(fig)
