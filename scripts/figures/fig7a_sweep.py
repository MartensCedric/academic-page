"""Figure 7, style A: rotating-ray filmstrip on an asymmetric open curve.

The curve and query point P are loaded from curve_source.svg. Across the four
frames the ray rotates; it stabs the scribble several times (blue = +1, red = -1),
but the signed sum S holds at +1 the whole way round — through both loops and every
tangency — and only steps to +2 once the ray sweeps past an endpoint.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import matplotlib.pyplot as plt

from utils import COLORS, setup_ax, save_fig
from endpoint_common import (CURVE, P_QUERY, draw_curve, draw_endpoints,
                             draw_query_point, draw_ray_and_hits)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig7a_sweep.svg",
))

XLIM = (-2.55, 2.55)
YLIM = (-1.5, 1.5)
RAY_LEN = 2.6
# Endpoint directions from P are ~5deg and ~177deg. The first three frames sit in
# the S=+1 sector; the fourth has just swept past the 5deg endpoint into S=+2.
FRAMES = [250, 340, 0, 30]

PANEL_H = 1.55
_agg = (XLIM[1] - XLIM[0]) / (YLIM[1] - YLIM[0])
fig, axes = plt.subplots(1, 4, figsize=(PANEL_H * _agg * 4, PANEL_H * 1.16))
fig.patch.set_facecolor(COLORS["background"])
fig.subplots_adjust(left=0.004, right=0.996, top=1.0, bottom=0.12, wspace=0.03)

prev_s, seq = None, []
for ax, deg in zip(axes, FRAMES):
    setup_ax(ax, fill_figure=False)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)

    draw_curve(ax, CURVE, arrow_frac=0.62, arrow_size=15)
    draw_endpoints(ax)
    s = draw_ray_and_hits(ax, P_QUERY, deg, CURVE, RAY_LEN, ray_lw=1.9,
                          marker_size=9)
    draw_query_point(ax, P_QUERY, label="")

    changed = prev_s is not None and s != prev_s
    s_str = f"{s:+d}" if s != 0 else "0"
    ax.text(0.5, -0.03, f"S = {s_str}", transform=ax.transAxes,
            ha="center", va="top", fontsize=16, fontweight="bold",
            color=COLORS["ray"] if changed else COLORS["polygon_edge"])
    seq.append((deg, s))
    prev_s = s

print("frames (deg, S):", seq)
save_fig(fig, OUTPUT)
plt.close(fig)
