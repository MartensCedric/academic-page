"""Shared scene + drawing helpers for the fig7 "the signed-intersection count
changes only at endpoints" figures (candidate styles A/B/C).

The scene — an asymmetric, self-intersecting open curve and a query point P — is
loaded from the editable ``curve_source.svg`` (see svg_curve.py / make_curve_svg.py).
Edit that SVG and re-run the fig7 scripts to redraw everything from the new curve.

A rotating ray can stab this scribble several times, yet the *signed* crossing
count it accumulates only ever changes when the ray sweeps past one of the two
endpoints — exactly what the One-Shot boundary term exploits.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np

from utils import COLORS, add_direction_arrow
from bezier import polyline, ray_signed_hits
from svg_curve import load_curve

# ── the scene, straight from the editable SVG ────────────────────────────────
CURVE, P_QUERY = load_curve()
ENDPTS = [(CURVE[0][0, 0], CURVE[0][0, 1]),      # start
          (CURVE[-1][3, 0], CURVE[-1][3, 1])]    # end


def endpoint_dirs(p=P_QUERY):
    """The two ray angles (deg) from ``p`` toward the curve's endpoints — the only
    directions at which the signed count can change."""
    return [float(np.degrees(np.arctan2(e[1] - p[1], e[0] - p[0])) % 360)
            for e in ENDPTS]


def deg_dir(deg):
    a = np.deg2rad(deg)
    return (float(np.cos(a)), float(np.sin(a)))


# ── drawing ───────────────────────────────────────────────────────────────────
def draw_curve(ax, segments=CURVE, arrow_frac=0.55, arrow_size=16):
    """``arrow_frac`` may be a single fraction or a sequence of fractions, each
    placing one orientation arrowhead along the curve."""
    x, y = polyline(segments, n=260)
    ax.plot(x, y, color=COLORS["polygon_edge"], lw=2.0, zorder=2,
            solid_capstyle="round")
    fracs = arrow_frac if np.iterable(arrow_frac) else (arrow_frac,)
    for frac in fracs:
        add_direction_arrow(ax, x, y, frac=frac, size=arrow_size)
    return x, y


def draw_endpoints(ax, pts=ENDPTS, size=9):
    """Hollow markers at the curve's open ends — where S is allowed to change."""
    for ex, ey in pts:
        ax.plot(ex, ey, "o", markersize=size, markerfacecolor="white",
                markeredgecolor=COLORS["polygon_edge"], markeredgewidth=1.8,
                zorder=4)


def draw_query_point(ax, p=P_QUERY, label="P", dx=0.10, dy=0.10, fontsize=13):
    ax.plot(p[0], p[1], "o", color=COLORS["polygon_edge"], markersize=7, zorder=6)
    if label:
        ax.text(p[0] + dx, p[1] + dy, label, fontsize=fontsize, fontweight="bold",
                color=COLORS["polygon_edge"], zorder=7)


def draw_ray_and_hits(ax, p, angle_deg, segments, ray_len, *, label_signs=False,
                      show_hits=True, ray_lw=1.6, marker_size=8, sign_fontsize=11,
                      sign_dy=0.16, sign_dx=0.0, ray_alpha=1.0):
    """Draw the ray from ``p`` at ``angle_deg`` and mark its signed crossings.

    Returns the signed sum S. Markers are colour-coded (blue +1, red -1); on a
    loopy curve the colour alone carries the sign, so ``label_signs`` defaults off.
    Pass ``show_hits=False`` to draw only the ray (S is still returned).
    """
    ux, uy = deg_dir(angle_deg)
    # Clip the ray to the axes box (with a small inset): annotate silently drops
    # the whole arrow when its tip lies outside the axes, and a clipped tip keeps
    # the arrowhead visible.
    inset = 0.05
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    t = ray_len
    for u, lo, hi, c in ((ux, x0 + inset, x1 - inset, p[0]),
                         (uy, y0 + inset, y1 - inset, p[1])):
        if u > 0:
            t = min(t, (hi - c) / u)
        elif u < 0:
            t = min(t, (lo - c) / u)
    end = (p[0] + ux * t, p[1] + uy * t)
    ax.annotate("", xy=end, xytext=(p[0], p[1]),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["ray"],
                                lw=ray_lw, mutation_scale=13, alpha=ray_alpha),
                zorder=3)
    hits = ray_signed_hits(segments, p, (ux, uy))
    s_sum = 0
    for hx, hy, sign in hits:
        s_sum += sign
        if not show_hits:
            continue
        color = COLORS["cross_pos"] if sign > 0 else COLORS["cross_neg"]
        ax.plot(hx, hy, "o", color=color, markersize=marker_size, zorder=5,
                markeredgecolor="white", markeredgewidth=0.9)
        if label_signs:
            ax.text(hx + sign_dx, hy + sign_dy, "+1" if sign > 0 else "−1",
                    fontsize=sign_fontsize, fontweight="bold", ha="center",
                    color=color, zorder=6)
    return s_sum
