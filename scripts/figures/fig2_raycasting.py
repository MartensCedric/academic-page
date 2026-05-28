"""Figure 2: Inside-outside test via raycasting."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib.pyplot as plt
from scene import VERTICES, POINT_A, POINT_B, XLIM, YLIM, FIGSIZE
from utils import (COLORS, setup_ax, save_fig, draw_polygon,
                   draw_labeled_point, ray_intersections_right)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig2_raycasting.svg",
))

fig, ax = plt.subplots(figsize=FIGSIZE)
setup_ax(ax)
draw_polygon(ax, VERTICES)
draw_labeled_point(ax, POINT_A, "A", COLORS["point_inside"])
draw_labeled_point(ax, POINT_B, "B", COLORS["point_outside"])

x_ray_end = XLIM[1] - 0.1

for point, pt_color in [(POINT_A, COLORS["point_inside"]),
                        (POINT_B, COLORS["point_outside"])]:
    x0, y0 = point
    # Ray arrow (start slightly past the dot so it doesn't overlap)
    ax.annotate(
        "", xy=(x_ray_end, y0), xytext=(x0 + 0.25, y0),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["ray"],
                        lw=1.5, mutation_scale=12),
        zorder=2,
    )
    # Intersection markers
    hits = ray_intersections_right(point, VERTICES)
    for x_hit in hits:
        ax.plot(x_hit, y0, "x", color=COLORS["ray"],
                markersize=10, markeredgewidth=2.5, zorder=5)
    # Intersection count label at end of ray
    parity = "odd" if len(hits) % 2 else "even"
    ax.text(x_ray_end + 0.05, y0 + 0.15,
            f"{len(hits)} ({parity})", fontsize=9,
            color=COLORS["ray"], zorder=4)

ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

save_fig(fig, OUTPUT)
plt.close(fig)
