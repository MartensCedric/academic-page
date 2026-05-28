"""Figure 1: Simple polygon with query points A (inside) and B (outside)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib.pyplot as plt
from scene import VERTICES, POINT_A, POINT_B, XLIM, YLIM, FIGSIZE
from utils import COLORS, setup_ax, save_fig, draw_polygon, draw_labeled_point

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig1_simple_polygon.svg",
))

fig, ax = plt.subplots(figsize=FIGSIZE)
setup_ax(ax)
draw_polygon(ax, VERTICES)
draw_labeled_point(ax, POINT_A, "A", COLORS["point_inside"])
draw_labeled_point(ax, POINT_B, "B", COLORS["point_outside"])
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

save_fig(fig, OUTPUT)
plt.close(fig)
