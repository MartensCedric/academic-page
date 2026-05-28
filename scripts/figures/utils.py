import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.size"] = 13

COLORS = {
    "polygon_fill": "#D6E4F0",
    "polygon_edge": "#2C3E50",
    "point_inside": "#E74C3C",
    "point_outside": "#27AE60",
    "ray": "#8E44AD",
    "background": "#FFFFFF",
}

FIGSIZE = (6, 5)


def setup_ax(ax):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_facecolor(COLORS["background"])


def save_fig(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor=COLORS["background"])
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
