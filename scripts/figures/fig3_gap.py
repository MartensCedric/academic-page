"""Figure 3: Gap in polygon causes raycasting to return the wrong answer.

Edge 6 (vertex 6 → vertex 7) is gapped. B's rightward ray normally crosses
edges 5→6 and 6→7 (2 hits, even → outside). With the gap, edge 6→7 is missing:
only 1 hit remains (odd → inside), which is wrong.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib.pyplot as plt
from scene import VERTICES, POINT_A, POINT_B, XLIM, YLIM, FIGSIZE
from utils import (COLORS, setup_ax, save_fig, draw_polygon_edges,
                   draw_labeled_point, ray_intersections_right)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig3_gap.svg",
))

GAP_EDGE = 6  # edge from vertex 6 (2.5, -0.2) to vertex 7 (3.879, 0.843)

fig, ax = plt.subplots(figsize=FIGSIZE)
setup_ax(ax)

# Open polygon — same style as fig1/fig2 but no fill and one edge missing
draw_polygon_edges(ax, VERTICES, skip_edge=GAP_EDGE)

draw_labeled_point(ax, POINT_A, "A", COLORS["point_inside"])
draw_labeled_point(ax, POINT_B, "B", COLORS["point_outside"])

# Ray from B (same as fig2)
x0, y0 = POINT_B
x_ray_end = XLIM[1] - 0.1
ax.annotate(
    "", xy=(x_ray_end, y0), xytext=(x0 + 0.25, y0),
    arrowprops=dict(arrowstyle="-|>", color=COLORS["ray"],
                    lw=1.5, mutation_scale=12),
    zorder=2,
)

# Intersections from the complete polygon (fig2 truth)
all_hits = ray_intersections_right(POINT_B, VERTICES)

# Intersections from the open polygon (gap removes edge 6)
open_vertices_hits = ray_intersections_right(
    POINT_B,
    [v for i, v in enumerate(VERTICES) if i != GAP_EDGE] + [VERTICES[GAP_EDGE]]
)
# Recompute properly: skip intersections that belong to the gapped edge
gapped_hit = None
for x_hit in all_hits:
    # Identify which hit came from the gapped edge
    i = GAP_EDGE
    j = (i + 1) % len(VERTICES)
    x1, y1 = VERTICES[i]
    x2, y2 = VERTICES[j]
    if (y1 <= y0 < y2) or (y2 <= y0 < y1):
        t = (y0 - y1) / (y2 - y1)
        x_edge = x1 + t * (x2 - x1)
        if abs(x_hit - x_edge) < 1e-9:
            gapped_hit = x_hit

visible_hits = [x for x in all_hits if x != gapped_hit]

# Mark visible (counted) intersections
for x_hit in visible_hits:
    ax.plot(x_hit, y0, "x", color=COLORS["ray"],
            markersize=10, markeredgewidth=2.5, zorder=5)

# Mark missed intersection as a ghost (where the gap is)
if gapped_hit is not None:
    ax.plot(gapped_hit, y0, "x", color=COLORS["ray"],
            markersize=10, markeredgewidth=2.5, alpha=0.25, zorder=5)

# Wrong-answer label
parity = "odd" if len(visible_hits) % 2 else "even"
ax.text(x_ray_end + 0.05, y0 + 0.15,
        f"{len(visible_hits)} ({parity})", fontsize=9,
        color=COLORS["ray"], zorder=4)

ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

save_fig(fig, OUTPUT)
plt.close(fig)
