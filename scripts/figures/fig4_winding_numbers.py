"""Figure 4: Integer winding numbers — 2x2 grid of oriented curves.

  ( 0) bumpy 3-lobe CCW, P outside      |  (+1) limacon CCW, P inside
  (-1) same limacon CW, P inside         |  (+2) limacon w/ inner loop, P in loop

Curves are deliberately non-circular. Panels +1 and -1 use the same shape
to isolate the effect of orientation on the sign.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
from utils import COLORS, setup_ax, save_fig, add_direction_arrow

OUTPUT = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    "../../assets/img/blog/one-shot-winding-numbers/fig4_winding_numbers.svg",
))

N = 500

def bumpy(r0, amp, k, ccw=True):
    """Polar curve r = r0 + amp*cos(k*t)."""
    t = np.linspace(0, 2*np.pi, N+1) if ccw else np.linspace(2*np.pi, 0, N+1)
    r = r0 + amp * np.cos(k * t)
    return r * np.cos(t), r * np.sin(t)

def limacon(a, b, dx=0.0, ccw=True):
    """r = a + b*cos(t), shifted horizontally by dx to centre in the panel."""
    t = np.linspace(0, 2*np.pi, N+1) if ccw else np.linspace(2*np.pi, 0, N+1)
    r = a + b * np.cos(t)
    return r * np.cos(t) + dx, r * np.sin(t)

# ── canvas shared by all 4 panels ────────────────────────────────────────────
XLIM = (-2.3, 2.3)
YLIM = (-2.3, 2.3)

# Limacon (a=1.0, b=0.8): natural bbox x ∈ [-0.2, 1.8] → shift -0.8 centres it
# Limacon w/ loop (a=0.3, b=1.4): inner loop = 1.1 wide (was 0.7), natural bbox
#   x ∈ [≈0, 1.7] → shift -0.84 centres it. Inner loop in world: x ∈ [-0.84, 0.26]
LIM_DX    = -0.8
INNER_DX  = -0.84

# Point positions (world coords, verified to be inside/outside each curve)
P_OUT    = (2.0,   0.5)   # outside bumpy shape  (max r ≈ 1.7)
P_IN     = (0.0,   0.4)   # inside shifted limacon (+1 / -1 panels)
P_INNER  = (-0.25, -0.2)  # inside inner loop (loop spans x ∈ [-0.84, 0.26], |y| < 0.6)

PANELS = [
    # WN = 0 ─ bumpy 3-lobe, P outside
    dict(wn=" 0",
         curves=[dict(xy=bumpy(1.2, 0.5, 3, ccw=True), arrows=[0.12])],
         point=P_OUT),

    # WN = +1 ─ limacon CCW, P inside
    dict(wn="+1",
         curves=[dict(xy=limacon(1.0, 0.8, dx=LIM_DX, ccw=True),  arrows=[0.20])],
         point=P_IN),

    # WN = −1 ─ same limacon CW, same P → sign flips
    dict(wn="−1",
         curves=[dict(xy=limacon(1.0, 0.8, dx=LIM_DX, ccw=False), arrows=[0.80])],
         point=P_IN),

    # WN = +2 ─ self-intersecting limacon CCW, P inside inner loop
    dict(wn="+2",
         curves=[dict(xy=limacon(0.3, 1.4, dx=INNER_DX, ccw=True), arrows=[0.10])],
         point=P_INNER),
]

# ── figure layout ─────────────────────────────────────────────────────────────
PANEL_SCALE = 0.60
_pw = (XLIM[1] - XLIM[0]) * PANEL_SCALE
_ph = (YLIM[1] - YLIM[0]) * PANEL_SCALE
FIGSIZE = (_pw * 2, _ph * 2)

fig, axes = plt.subplots(2, 2, figsize=FIGSIZE)
fig.patch.set_facecolor(COLORS["background"])
fig.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0.05, hspace=0.05)

cx = (XLIM[0] + XLIM[1]) / 2

for ax, panel in zip(axes.flat, PANELS):
    setup_ax(ax, fill_figure=False)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)

    for curve in panel["curves"]:
        x, y = curve["xy"]
        ax.plot(x, y, color=COLORS["polygon_edge"], lw=2.0, zorder=1)
        for frac in curve["arrows"]:
            add_direction_arrow(ax, x, y, frac, size=24)

    px, py = panel["point"]
    ax.plot(px, py, "o", color=COLORS["polygon_edge"], markersize=7, zorder=3)
    ax.text(px + 0.12, py + 0.15, "P",
            fontsize=12, fontweight="bold", color=COLORS["polygon_edge"], zorder=4)

    ax.text(cx, YLIM[0] + 0.25, f"WN = {panel['wn']}",
            fontsize=13, fontweight="bold", ha="center",
            color=COLORS["polygon_edge"], zorder=4)

save_fig(fig, OUTPUT)
plt.close(fig)
