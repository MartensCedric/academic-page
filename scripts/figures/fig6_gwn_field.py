"""Figure 6: GWN field converges as the number of averaging rays grows.

Three 256x256 panels show the *same* open, oriented bezier curve (a near-circle
with a gap). Each panel's background is the generalized winding number field,
estimated per pixel as the average signed ray-crossing count over 1, 5, then 25
ray directions. Ray/curve intersections use bezier clipping (see bezier.py).
With one ray the field is blocky and integer-valued (note the wedge artifact off
the gap); averaging more directions converges to the smooth fractional GWN.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from utils import (COLORS, setup_ax, save_fig, add_direction_arrow,
                   GWN_CMAP, GWN_NORM, add_gwn_colorbar)
from bezier import make_open_arc, polyline, gwn_field

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig6_gwn_field.svg",
))

RES = 256
BOUNDS = (-1.3, 1.3)
RAY_COUNTS = [1, 5, 25]

# Open CCW near-circle: 290 deg sweep starting at 35 deg leaves a ~70 deg gap
# centred on the +x axis (the right side), where the orientation arrow shows.
CURVE = make_open_arc(center=(0.0, 0.0), radius=0.95,
                      start_deg=35, sweep_deg=290, ccw=True, n_seg=4)

xs = np.linspace(BOUNDS[0], BOUNDS[1], RES)
ys = np.linspace(BOUNDS[0], BOUNDS[1], RES)
curve_x, curve_y = polyline(CURVE, n=300)

# ── figure layout: [colorbar | panel | panel | panel] ────────────────────────
PANEL_IN = 2.4
fig = plt.figure(figsize=(PANEL_IN * 3 + 0.9, PANEL_IN + 0.35))
fig.patch.set_facecolor(COLORS["background"])
gs = GridSpec(1, 4, width_ratios=[0.05, 1, 1, 1], wspace=0.22,
              left=0.035, right=0.98, top=0.88, bottom=0.08)

cax = fig.add_subplot(gs[0, 0])

for col, n_rays in enumerate(RAY_COUNTS, start=1):
    print(f"Computing GWN field with {n_rays} ray(s)...")
    field = gwn_field(CURVE, xs, ys, n_rays)

    ax = fig.add_subplot(gs[0, col])
    setup_ax(ax, fill_figure=False)
    ax.imshow(field, origin="lower", extent=[*BOUNDS, *BOUNDS],
              cmap=GWN_CMAP, norm=GWN_NORM, interpolation="nearest", zorder=0)
    ax.plot(curve_x, curve_y, color=COLORS["polygon_edge"], lw=2.0, zorder=2)
    add_direction_arrow(ax, curve_x, curve_y, frac=0.30, size=22)
    ax.set_xlim(*BOUNDS)
    ax.set_ylim(*BOUNDS)
    label = "1 ray" if n_rays == 1 else f"{n_rays} rays"
    ax.set_title(label, fontsize=14, fontweight="bold",
                 color=COLORS["polygon_edge"])

add_gwn_colorbar(fig, cax)

save_fig(fig, OUTPUT)
plt.close(fig)
