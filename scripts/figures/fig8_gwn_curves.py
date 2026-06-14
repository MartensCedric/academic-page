"""Figure 8: exact GWN fields for three different curves.

Three 256x256 panels, each showing the exact generalized winding number field
(computed per pixel with the turning-angle formula — see bezier.gwn_field_exact)
of a curve inspired by the SGP 2025 talk:

  1. an open bean-shaped curve with a gap — the field is ~1 inside and leaks
     smoothly through the opening;
  2. a closed figure-eight — GWN reduces to the integer winding number, with a
     +1 loop and a -1 loop;
  3. an open inward spiral — winding accumulates, exceeding 2 at the core.

The colormap extends the shared GWN diverging map past +1 so the spiral's core
reads as a deeper green; the colorbar covers [-1, 2.5] with integer ticks.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec

from utils import (COLORS, setup_ax, save_fig, add_direction_arrow,
                   add_gwn_colorbar)
from bezier import catmull_rom, polyline, gwn_field_exact

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig8_gwn_curves.svg",
))

RES = 256
BOUNDS = (-1.3, 1.3)

# Extended diverging map: red (-1) → white (0) → green (+1) → deep green (+2.5).
VMIN, VMAX = -1.0, 2.5
EXT_CMAP = LinearSegmentedColormap.from_list("gwn_ext", [
    (0.0, COLORS["field_neg"]),
    ((0.0 - VMIN) / (VMAX - VMIN), COLORS["background"]),
    ((1.0 - VMIN) / (VMAX - VMIN), COLORS["field_pos"]),
    (1.0, COLORS["field_pos2"]),
])
EXT_NORM = Normalize(vmin=VMIN, vmax=VMAX)


# ── the three curves (dense polylines) ────────────────────────────────────────
def bean_curve():
    """Open bean: a smooth CCW blob with a dent on the right and a gap at it."""
    pts = [
        (0.62, 0.52),    # start: upper lip of the gap
        (0.10, 0.92),
        (-0.65, 0.78),
        (-1.00, 0.10),
        (-0.78, -0.55),
        (-0.10, -0.95),
        (0.55, -0.78),
        (0.92, -0.32),
        (0.38, 0.10),    # end: dent tip, lower lip of the gap
    ]
    return polyline(catmull_rom(pts, closed=False), n=200)


def eight_curve():
    """Closed figure-eight: top loop CCW (+1), bottom loop CW (-1)."""
    t = np.linspace(0.0, 2.0 * np.pi, 1400)
    return 0.62 * np.sin(2.0 * t), 0.95 * np.sin(t)


def spiral_curve():
    """Open CCW spiral, 2.4 turns inward — GWN exceeds 2 at the core."""
    t = np.linspace(0.0, 1.0, 1500)
    theta = np.deg2rad(100.0) + 2.0 * np.pi * 2.4 * t
    r = 1.08 - 0.72 * t
    return r * np.cos(theta), r * np.sin(theta)


# (x, y, orientation-arrow fractions, is_open)
PANELS = [
    (*bean_curve(), (0.30, 0.75), True),
    (*eight_curve(), (0.20, 0.70), False),
    (*spiral_curve(), (0.15, 0.55, 0.90), True),
]

xs = np.linspace(BOUNDS[0], BOUNDS[1], RES)
ys = np.linspace(BOUNDS[0], BOUNDS[1], RES)

# ── figure layout: [colorbar | panel | panel | panel] ────────────────────────
PANEL_IN = 2.4
fig = plt.figure(figsize=(PANEL_IN * 3 + 0.9, PANEL_IN + 0.25))
fig.patch.set_facecolor(COLORS["background"])
gs = GridSpec(1, 4, width_ratios=[0.05, 1, 1, 1], wspace=0.22,
              left=0.035, right=0.98, top=0.93, bottom=0.05)

cax = fig.add_subplot(gs[0, 0])

for col, (cx, cy, arrow_fracs, is_open) in enumerate(PANELS, start=1):
    print(f"Computing exact GWN field for panel {col}...")
    field = gwn_field_exact(cx, cy, xs, ys)

    ax = fig.add_subplot(gs[0, col])
    setup_ax(ax, fill_figure=False)
    ax.imshow(field, origin="lower", extent=[*BOUNDS, *BOUNDS],
              cmap=EXT_CMAP, norm=EXT_NORM, interpolation="nearest", zorder=0)
    ax.plot(cx, cy, color=COLORS["polygon_edge"], lw=2.0, zorder=2,
            solid_capstyle="round")
    for frac in arrow_fracs:
        add_direction_arrow(ax, cx, cy, frac=frac, size=18)
    if is_open:
        for ex, ey in ((cx[0], cy[0]), (cx[-1], cy[-1])):
            ax.plot(ex, ey, "o", markersize=7, markerfacecolor="white",
                    markeredgecolor=COLORS["polygon_edge"],
                    markeredgewidth=1.6, zorder=4)
    ax.set_xlim(*BOUNDS)
    ax.set_ylim(*BOUNDS)

add_gwn_colorbar(fig, cax, cmap=EXT_CMAP, norm=EXT_NORM, ticks=(-1, 0, 1, 2))

save_fig(fig, OUTPUT)
if "--png" in sys.argv:   # dev preview
    fig.savefig("/tmp/fig8_preview.png", dpi=150, bbox_inches=None,
                facecolor=COLORS["background"])
    print("Saved: /tmp/fig8_preview.png")
plt.close(fig)
