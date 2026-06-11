import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.colors import LinearSegmentedColormap, Normalize

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.size"] = 13

COLORS = {
    "polygon_fill": "#D6E4F0",
    "polygon_edge": "#2C3E50",
    "point_inside": "#E74C3C",
    "point_outside": "#27AE60",
    "ray": "#8E44AD",
    "background": "#FFFFFF",
    # Signed ray/curve crossings: blue = +1, red = -1 (shared by fig5 and fig7).
    "cross_pos": "#2980B9",
    "cross_neg": "#E74C3C",
    # Generalized-winding-number field: low-saturation diverging ends.
    "field_pos": "#6Fae8c",   # GWN = +1 (inside, soft green)
    "field_neg": "#cf8b8b",   # GWN = -1 (soft red)
}

# Reusable diverging colormap for GWN fields: red (-1) → white (0) → green (+1).
GWN_CMAP = LinearSegmentedColormap.from_list(
    "gwn", [COLORS["field_neg"], COLORS["background"], COLORS["field_pos"]]
)
GWN_NORM = Normalize(vmin=-1.0, vmax=1.0)


def add_gwn_colorbar(fig, cax, label="GWN"):
    """Draw the GWN colorbar (ticks -1/0/+1) into the provided axes `cax`.

    Ticks/labels sit on the right of the bar so nothing is clipped when the
    colorbar is placed at the very left of a figure; `label` is a short title."""
    sm = mpl.cm.ScalarMappable(norm=GWN_NORM, cmap=GWN_CMAP)
    cb = fig.colorbar(sm, cax=cax, ticks=[-1, 0, 1])
    cax.yaxis.set_ticks_position("right")
    cax.yaxis.set_label_position("right")
    cb.ax.tick_params(labelsize=10)
    cb.outline.set_linewidth(0.8)
    if label:
        cax.set_title(label, fontsize=11, fontweight="bold", pad=6)
    return cb

def setup_ax(ax, fill_figure=True):
    """Configure ax for a clean figure.

    fill_figure=True  (default) — axes fills the whole figure; use for
                                  single-axes figures whose FIGSIZE is derived
                                  from the data extent (scene.SCALE pattern).
    fill_figure=False           — leave layout to matplotlib; use for subplot
                                  grids where each ax is one cell.
    """
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(COLORS["background"])
    if fill_figure:
        ax.set_position([0, 0, 1, 1])


def save_fig(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # No tight-crop: the figure dimensions ARE the canvas. All figures in a
    # set share the same FIGSIZE (derived from the same XLIM/YLIM/SCALE), so
    # their SVGs are identical in size regardless of content.
    fig.savefig(path, bbox_inches=None, facecolor=COLORS["background"])
    print(f"Saved: {path}")


def draw_polygon(ax, vertices):
    ax.add_patch(MplPolygon(
        vertices, closed=True,
        facecolor=COLORS["polygon_fill"],
        edgecolor=COLORS["polygon_edge"],
        linewidth=2.0, zorder=1,
    ))


def draw_labeled_point(ax, point, label, color):
    ax.plot(*point, "o", color=color, markersize=9, zorder=3)
    ax.text(point[0] + 0.15, point[1] + 0.15, label,
            fontsize=15, fontweight="bold", color=color, zorder=4)


def add_direction_arrow(ax, x, y, frac=0.25, size=12):
    """Place an orientation arrowhead at fractional position along curve (x, y).

    size controls the arrowhead display size (mutation_scale); increase for
    figures where the direction must be immediately obvious.

    Uses a central-difference tangent and a visible data-space separation so
    matplotlib can determine the arrow direction accurately. The short shaft is
    the same colour as the curve and blends in visually.
    """
    n = len(x)
    i = int(frac * n) % n
    # Central difference: accurate tangent even near high-curvature regions
    step = max(2, n // 200)
    i_prev = (i - step) % n
    i_next = (i + step) % n
    dx, dy = float(x[i_next] - x[i_prev]), float(y[i_next] - y[i_prev])
    L = (dx ** 2 + dy ** 2) ** 0.5
    if L < 1e-12:
        return
    ux, uy = dx / L, dy / L
    # Visible separation in data coords so the display-space direction is
    # well-defined. The shaft overlaps the curve (same colour) and disappears.
    sep = 0.12
    ax.annotate(
        "",
        xy=(float(x[i]) + ux * sep, float(y[i]) + uy * sep),
        xytext=(float(x[i]) - ux * sep, float(y[i]) - uy * sep),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["polygon_edge"],
                        lw=2.0, mutation_scale=size),
        zorder=5,
    )


def add_edge_arrow(ax, v1, v2, size=12):
    """Place an orientation arrow at the midpoint of the straight edge v1→v2."""
    mx, my = (v1[0] + v2[0]) / 2, (v1[1] + v2[1]) / 2
    dx, dy = v2[0] - v1[0], v2[1] - v1[1]
    L = (dx ** 2 + dy ** 2) ** 0.5
    if L < 1e-12:
        return
    ux, uy = dx / L, dy / L
    sep = 0.12
    ax.annotate(
        "",
        xy=(mx + ux * sep, my + uy * sep),
        xytext=(mx - ux * sep, my - uy * sep),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["polygon_edge"],
                        lw=2.0, mutation_scale=size),
        zorder=5,
    )


def draw_polygon_edges(ax, vertices, skip_edge=None):
    """Draw polygon as individual edge segments (no fill). skip_edge omits one edge by index."""
    n = len(vertices)
    for i in range(n):
        if i == skip_edge:
            continue
        j = (i + 1) % n
        ax.plot(
            [vertices[i][0], vertices[j][0]],
            [vertices[i][1], vertices[j][1]],
            color=COLORS["polygon_edge"], linewidth=2.0,
            solid_capstyle="round", zorder=1,
        )


def ray_signed_intersections_right(origin, vertices):
    """(x, sign) pairs where sign=+1 for upward crossing, -1 for downward."""
    x0, y0 = origin
    n = len(vertices)
    hits = []
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if y1 <= y0 < y2:
            t = (y0 - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            if x > x0:
                hits.append((x, +1))
        elif y2 <= y0 < y1:
            t = (y0 - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            if x > x0:
                hits.append((x, -1))
    return sorted(hits, key=lambda h: h[0])


def ray_intersections_right(origin, vertices):
    """x-coords where a rightward horizontal ray from origin crosses the polygon edges."""
    x0, y0 = origin
    n = len(vertices)
    hits = []
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if (y1 <= y0 < y2) or (y2 <= y0 < y1):
            t = (y0 - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            if x > x0:
                hits.append(x)
    return sorted(hits)
