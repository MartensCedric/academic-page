"""Seed the editable curve source ``curve_source.svg``.

Run once to (re)generate the SVG that the fig7 scripts read. After this, the SVG
is the source of truth: edit the path / move the query circle in any vector editor
and re-run the fig7 scripts — you do NOT need to touch this generator again.

The curve is an asymmetric, self-intersecting open scribble built as a Catmull-Rom
spline through a handful of anchor points; the query point P sits where a rotating
ray stabs the curve richly. Coordinates are written in SVG space via svg_curve's
fixed transform so the file looks upright in an editor.
"""
import os
import numpy as np
from svg_curve import to_svg, SCALE, OX, OY, load_curve

OUT = os.path.join(os.path.dirname(__file__), "curve_source.svg")

# Asymmetric scribble: two unequal loops + trailing ends (math space).
# Authored as a list of anchors, then reversed so the traversal winds the query
# point positively (signed counts come out +1 / +2 rather than negative).
ANCHORS = [(-2.25, 0.15), (-1.45, 0.95), (-0.45, 1.05), (0.25, 0.3),
           (-0.35, -0.4), (-0.95, 0.2), (-0.2, 0.9), (0.8, 0.62),
           (1.35, -0.2), (0.85, -1.0), (-0.05, -1.05), (-0.45, -0.3),
           (0.55, -0.2), (1.45, -0.5), (2.2, 0.25)][::-1]
QUERY = (-0.2, 0.05)


def catmull_segments(pts, tension=0.0):
    P = [np.asarray(p, float) for p in pts]
    ext = [P[0]] + P + [P[-1]]
    c = (1.0 - tension) / 6.0
    segs = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        segs.append([p1, p1 + (p2 - p0) * c, p2 - (p3 - p1) * c, p2])
    return segs


def path_d(segs):
    s0 = segs[0][0]
    x0, y0 = to_svg(*s0)
    parts = [f"M {x0:.2f},{y0:.2f}"]
    for p0, p1, p2, p3 in segs:
        c1 = to_svg(*p1); c2 = to_svg(*p2); c3 = to_svg(*p3)
        parts.append(f"C {c1[0]:.2f},{c1[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} "
                     f"{c3[0]:.2f},{c3[1]:.2f}")
    return " ".join(parts)


segs = catmull_segments(ANCHORS)
qx, qy = to_svg(*QUERY)

# viewBox padded around the content
xs = [to_svg(*p)[0] for s in segs for p in s]
ys = [to_svg(*p)[1] for s in segs for p in s]
pad = 30
minx, miny = min(xs) - pad, min(ys) - pad
w, h = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad

svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- fig7 demo curve. Edit the path's d and/or move the query circle, then re-run
     the fig7 scripts. Transform to math space: x=(sx-{OX:.0f})/{SCALE:.0f}, y=-(sy-{OY:.0f})/{SCALE:.0f}. -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.1f} {miny:.1f} {w:.1f} {h:.1f}" width="{w:.1f}" height="{h:.1f}">
  <path id="curve" fill="none" stroke="#2C3E50" stroke-width="3"
        d="{path_d(segs)}"/>
  <circle id="query" cx="{qx:.2f}" cy="{qy:.2f}" r="5" fill="#8E44AD"/>
</svg>
"""

with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}")

# sanity: round-trip load
rsegs, rq = load_curve(OUT)
print(f"loaded {len(rsegs)} segments, query={tuple(round(v,3) for v in rq)}")
