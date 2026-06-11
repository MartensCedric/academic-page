"""Figure 7, style C: the query point's directions, partitioned into sectors.

The asymmetric open curve (from curve_source.svg) with P inside its loops. The two
rays from P through the curve's endpoints split every ray direction into just two
sectors. Within a sector the signed-intersection count is constant — even though
individual rays stab the curve anywhere from once to five times. Aim a ray into the
upper sector and the signed sum is +2; into the lower one and it is +1. The only
places the count changes are the sector boundaries: the endpoint directions.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

from utils import COLORS, setup_ax, save_fig
from endpoint_common import (CURVE, P_QUERY, endpoint_dirs, deg_dir, draw_curve,
                             draw_endpoints, draw_query_point, draw_ray_and_hits)

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig7c_sectors.svg",
))

XLIM = (-2.65, 2.65)
YLIM = (-1.75, 1.75)
RAY_LEN = 2.5
WEDGE_R = 6.0

d_lo, d_hi = sorted(endpoint_dirs(P_QUERY))   # ~5deg and ~177deg

fig, ax = plt.subplots(figsize=((XLIM[1] - XLIM[0]) * 0.86, (YLIM[1] - YLIM[0]) * 0.86))
fig.patch.set_facecolor(COLORS["background"])
setup_ax(ax, fill_figure=False)
ax.set_xlim(*XLIM)
ax.set_ylim(*YLIM)

# ── shaded sectors (behind everything): upper = S+2, lower = S+1 ─────────────
ax.add_patch(Wedge(P_QUERY, WEDGE_R, d_lo, d_hi, facecolor=COLORS["field_pos"],
                   alpha=0.42, edgecolor="none", zorder=0))
ax.add_patch(Wedge(P_QUERY, WEDGE_R, d_hi, d_lo + 360, facecolor=COLORS["field_pos"],
                   alpha=0.18, edgecolor="none", zorder=0))

# ── boundary rays through the endpoints (dashed) ─────────────────────────────
for deg in (d_lo, d_hi):
    ux, uy = deg_dir(deg)
    ax.plot([P_QUERY[0], P_QUERY[0] + ux * RAY_LEN],
            [P_QUERY[1], P_QUERY[1] + uy * RAY_LEN],
            color=COLORS["polygon_edge"], lw=1.4, ls=(0, (4, 3)), zorder=3)

# ── a couple of sample rays inside each sector ───────────────────────────────
for deg in [60, 120, 235, 300]:
    draw_ray_and_hits(ax, P_QUERY, deg, CURVE, RAY_LEN, show_hits=False,
                      ray_lw=1.2, ray_alpha=0.6)

# ── curve, endpoints, query point ────────────────────────────────────────────
draw_curve(ax, CURVE, arrow_frac=0.62, arrow_size=17)
draw_endpoints(ax)
draw_query_point(ax, P_QUERY, dx=-0.12, dy=0.16)

# ── sector labels ─────────────────────────────────────────────────────────────
ax.text(-1.3, 1.4, "S = +2", fontsize=15, fontweight="bold",
        color="#3f8a63", ha="center", zorder=8)
ax.text(0.7, -1.5, "S = +1", fontsize=14, fontweight="bold",
        color="#3f8a63", ha="center", zorder=8)

save_fig(fig, OUTPUT)
plt.close(fig)
