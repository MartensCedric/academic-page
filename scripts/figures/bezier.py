"""Cubic-bezier helpers + ray/curve intersection via bezier clipping.

A curve is represented as a list of cubic segments, each an ``(4, 2)`` array of
control points ``[P0, P1, P2, P3]``. The headline routine is
``ray_segment_signed_crossings``, which finds where a ray meets one cubic
segment using **bezier clipping** (Sederberg & Nishita): the signed distance of
the curve to the ray line is itself a 1-D cubic bezier, and its roots on [0, 1]
are isolated by repeatedly clipping the parameter interval to the span where the
control polygon's convex hull can cross zero.
"""
import numpy as np


# ── construction ──────────────────────────────────────────────────────────────
def make_open_arc(center, radius, start_deg, sweep_deg, ccw=True, n_seg=4):
    """Cubic-bezier approximation of a circular arc, left **open** (a gap).

    Returns a list of (4, 2) control-point arrays. The arc spans ``sweep_deg``
    starting at ``start_deg``; a sweep < 360 leaves a gap, so the curve is open.
    Each segment covers an equal angular slice (<= 90 deg for a good fit) and
    uses the standard tangent-handle length ``(4/3) * tan(dtheta / 4) * radius``.
    """
    cx, cy = center
    sweep = np.deg2rad(sweep_deg) * (1 if ccw else -1)
    a0 = np.deg2rad(start_deg)
    dtheta = sweep / n_seg
    k = (4.0 / 3.0) * np.tan(dtheta / 4.0)  # handle length / radius

    segments = []
    for s in range(n_seg):
        t0 = a0 + s * dtheta
        t1 = t0 + dtheta
        p0 = np.array([cx + radius * np.cos(t0), cy + radius * np.sin(t0)])
        p3 = np.array([cx + radius * np.cos(t1), cy + radius * np.sin(t1)])
        # Tangents point along the direction of travel (sign of dtheta).
        tan0 = np.array([-np.sin(t0), np.cos(t0)]) * np.sign(dtheta)
        tan1 = np.array([-np.sin(t1), np.cos(t1)]) * np.sign(dtheta)
        p1 = p0 + tan0 * abs(k) * radius
        p2 = p3 - tan1 * abs(k) * radius
        segments.append(np.array([p0, p1, p2, p3]))
    return segments


def catmull_rom(points, closed=False):
    """Uniform Catmull-Rom spline through ``points`` as cubic bezier segments.

    Returns a list of (4, 2) control-point arrays, one per consecutive point
    pair (wrapping around when ``closed``). Uses the standard CR-to-bezier
    handle map: the handle at each point is ``(next - prev) / 6``. Open curves
    clamp the end tangents to the boundary points.
    """
    pts = [np.asarray(p, dtype=float) for p in points]
    n = len(pts)
    count = n if closed else n - 1
    segs = []
    for i in range(count):
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p0 = pts[(i - 1) % n] if (closed or i > 0) else p1
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        segs.append(np.array([p1, p1 + (p2 - p0) / 6.0,
                              p2 - (p3 - p1) / 6.0, p2]))
    return segs


# ── evaluation ────────────────────────────────────────────────────────────────
def eval_segment(P, t):
    """De Casteljau evaluation of one cubic segment at scalar/array ``t``."""
    t = np.asarray(t, dtype=float)
    mt = 1.0 - t
    b0 = mt ** 3
    b1 = 3 * mt ** 2 * t
    b2 = 3 * mt * t ** 2
    b3 = t ** 3
    x = b0 * P[0, 0] + b1 * P[1, 0] + b2 * P[2, 0] + b3 * P[3, 0]
    y = b0 * P[0, 1] + b1 * P[1, 1] + b2 * P[2, 1] + b3 * P[3, 1]
    return x, y


def deriv_segment(P, t):
    """Tangent (dx/dt, dy/dt) of one cubic segment at scalar ``t``."""
    t = float(t)
    mt = 1.0 - t
    # B'(t) = 3[ (P1-P0) mt^2 + 2(P2-P1) mt t + (P3-P2) t^2 ]
    d = 3 * ((P[1] - P[0]) * mt ** 2
             + 2 * (P[2] - P[1]) * mt * t
             + (P[3] - P[2]) * t ** 2)
    return d


def polyline(segments, n=200):
    """Concatenate dense samples of all segments into ``(x, y)`` arrays."""
    xs, ys = [], []
    for P in segments:
        t = np.linspace(0.0, 1.0, n)
        x, y = eval_segment(P, t)
        xs.append(x)
        ys.append(y)
    return np.concatenate(xs), np.concatenate(ys)


# ── bezier clipping (1-D root finding) ────────────────────────────────────────
def _de_casteljau_subdiv(d, t0, t1):
    """Return the 4 control values of the 1-D cubic ``d`` restricted to [t0, t1]."""
    def split_right(c, t):  # keep [t, 1]
        a, b, e, f = c
        ab, be, ef = a + (b - a) * t, b + (e - b) * t, e + (f - e) * t
        abe, bef = ab + (be - ab) * t, be + (ef - be) * t
        abef = abe + (bef - abe) * t
        return [abef, bef, ef, f]

    def split_left(c, t):   # keep [0, t]
        a, b, e, f = c
        ab, be, ef = a + (b - a) * t, b + (e - b) * t, e + (f - e) * t
        abe, bef = ab + (be - ab) * t, be + (ef - be) * t
        abef = abe + (bef - abe) * t
        return [a, ab, abe, abef]

    c = split_right(d, t0)
    # After cropping the left end at t0, the original t1 maps to a new local param.
    tt = (t1 - t0) / (1.0 - t0) if t1 < 1.0 else 1.0
    c = split_left(c, tt)
    return c


def _convex_hull(pts):
    """Ordered convex-hull vertices of ``pts`` (already sorted by x), via the
    monotone-chain algorithm. Returns the hull as a closed ring of points."""
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _hull_zero_span(d):
    """Param span [lo, hi] in [0,1] where the convex hull of the control points
    ``(i/3, d_i)`` crosses value 0. Returns None if the hull excludes 0. The
    Bezier curve lies inside this hull, so every root sits within [lo, hi]."""
    if min(d) > 0 or max(d) < 0:
        return None
    pts = [(i / 3.0, d[i]) for i in range(4)]
    hull = _convex_hull(pts)
    lo, hi = None, None
    n = len(hull)
    for i in range(n):
        x1, y1 = hull[i]
        x2, y2 = hull[(i + 1) % n]
        if (y1 <= 0 <= y2) or (y2 <= 0 <= y1):
            if y1 == y2:
                cs = (x1, x2)
            else:
                cs = (x1 + (0 - y1) / (y2 - y1) * (x2 - x1),)
            for xc in cs:
                lo = xc if lo is None else min(lo, xc)
                hi = xc if hi is None else max(hi, xc)
    if lo is None:
        return None
    return max(0.0, lo), min(1.0, hi)


def bezier_clip_roots(d, tol=1e-7, max_iter=60):
    """Roots in [0, 1] of the 1-D cubic bezier with control values ``d[0..3]``.

    Implements bezier clipping: clip the interval to the convex-hull zero span;
    when clipping stalls (interval barely shrinks) the segment likely holds
    multiple roots, so split at the midpoint and recurse.
    """
    roots = []
    # Work queue of (control values on [a,b], a, b, iteration count).
    stack = [(list(map(float, d)), 0.0, 1.0, 0)]
    while stack:
        c, a, b, it = stack.pop()
        if b - a < tol:
            roots.append(0.5 * (a + b))
            continue
        if it > max_iter:
            roots.append(0.5 * (a + b))
            continue
        span = _hull_zero_span(c)
        if span is None:
            continue
        lo, hi = span
        # If the clip removes little, split to separate multiple roots.
        if hi - lo > 0.8:
            mid = 0.5
            left = _de_casteljau_subdiv(c, 0.0, mid)
            right = _de_casteljau_subdiv(c, mid, 1.0)
            am, bm = a + (b - a) * mid, b
            stack.append((right, am, bm, it + 1))
            stack.append((left, a, a + (b - a) * mid, it + 1))
        else:
            clipped = _de_casteljau_subdiv(c, lo, hi)
            na = a + (b - a) * lo
            nb = a + (b - a) * hi
            stack.append((clipped, na, nb, it + 1))
    # Deduplicate roots that split-recursion may have found twice.
    roots.sort()
    out = []
    for r in roots:
        if not out or abs(r - out[-1]) > 1e-5:
            out.append(r)
    return out


# ── ray / curve signed crossings ──────────────────────────────────────────────
def ray_segment_signed_crossings(P, origin, u):
    """Signed count of crossings of ray ``origin + s*u`` (s > 0) with cubic ``P``.

    Sign convention: ``+1`` when the curve's tangent has a positive component
    along the ray's left normal ``n = (-u_y, u_x)`` at the crossing, ``-1``
    otherwise — i.e. CCW interior accumulates +1.
    """
    ox, oy = origin
    ux, uy = u
    nx, ny = -uy, ux
    # 1-D signed-distance control values to the ray line through origin.
    d = [nx * (P[i, 0] - ox) + ny * (P[i, 1] - oy) for i in range(4)]
    if min(d) > 0 or max(d) < 0:   # convex hull excludes 0 — no crossing
        return 0
    total = 0
    for t in bezier_clip_roots(d):
        bx, by = eval_segment(P, t)
        s = ux * (float(bx) - ox) + uy * (float(by) - oy)
        if s <= 0:
            continue
        tan = deriv_segment(P, t)
        total += 1 if (nx * tan[0] + ny * tan[1]) > 0 else -1
    return total


def ray_signed_hits(segments, origin, u):
    """List of ``(x, y, sign)`` where the ray ``origin + s*u`` (s > 0) meets the curve.

    Same sign convention as ``ray_segment_signed_crossings`` (CCW interior → +1), but
    returns the actual crossing points so they can be plotted. Results are sorted by
    distance ``s`` along the ray.
    """
    ox, oy = origin
    ux, uy = u
    nx, ny = -uy, ux
    hits = []
    for P in segments:
        d = [nx * (P[i, 0] - ox) + ny * (P[i, 1] - oy) for i in range(4)]
        if min(d) > 0 or max(d) < 0:   # convex hull excludes 0 — no crossing
            continue
        for t in bezier_clip_roots(d):
            bx, by = eval_segment(P, t)
            bx, by = float(bx), float(by)
            s = ux * (bx - ox) + uy * (by - oy)
            if s <= 0:
                continue
            tan = deriv_segment(P, t)
            sign = 1 if (nx * tan[0] + ny * tan[1]) > 0 else -1
            hits.append((s, bx, by, sign))
    hits.sort(key=lambda h: h[0])
    return [(bx, by, sign) for _s, bx, by, sign in hits]


def gwn_at(segments, p, n_rays):
    """GWN estimate at point ``p`` = mean signed crossings over ``n_rays`` dirs."""
    angles = np.arange(n_rays) * (2 * np.pi / n_rays)
    acc = 0.0
    for a in angles:
        u = (np.cos(a), np.sin(a))
        acc += sum(ray_segment_signed_crossings(P, p, u) for P in segments)
    return acc / n_rays


def gwn_field_exact(px, py, xs, ys):
    """Exact GWN field of the polyline ``(px, py)`` on the grid ``xs`` × ``ys``.

    Uses the turning-angle formula ``w(p) = (1/2π) Σ ∠(v_i - p, v_{i+1} - p)``:
    each polyline edge contributes the signed angle it subtends at the query
    point. Exact for the polyline, so dense samples of a smooth curve converge
    to its GWN. A closed curve must repeat its first point at the end.
    """
    GX, GY = np.meshgrid(xs, ys)          # (ny, nx)
    total = np.zeros_like(GX)
    ax, ay = px[0] - GX, py[0] - GY
    for i in range(1, len(px)):
        bx, by = px[i] - GX, py[i] - GY
        total += np.arctan2(ax * by - ay * bx, ax * bx + ay * by)
        ax, ay = bx, by
    return total / (2.0 * np.pi)


def gwn_field(segments, xs, ys, n_rays):
    """GWN field on the grid ``xs`` × ``ys`` (shape ``(len(ys), len(xs))``).

    For each (direction, segment) the pixels whose signed-distance control values
    all share one sign are rejected in bulk with numpy (their convex hull cannot
    reach 0), and the scalar bezier clipper runs only on the surviving band.
    """
    nx_grid, ny_grid = len(xs), len(ys)
    GX, GY = np.meshgrid(xs, ys)          # (ny, nx)
    field = np.zeros((ny_grid, nx_grid), dtype=float)
    angles = np.arange(n_rays) * (2 * np.pi / n_rays)

    for a in angles:
        ux, uy = float(np.cos(a)), float(np.sin(a))
        nx, ny = -uy, ux
        for P in segments:
            # Signed distance of each control point to the ray line, per pixel.
            d = [nx * (P[i, 0] - GX) + ny * (P[i, 1] - GY) for i in range(4)]
            dmin = np.minimum.reduce(d)
            dmax = np.maximum.reduce(d)
            candidate = (dmin <= 0) & (dmax >= 0)   # hull may cross zero
            rows, cols = np.nonzero(candidate)
            for r, c in zip(rows, cols):
                ox, oy = GX[r, c], GY[r, c]
                dv = [d[i][r, c] for i in range(4)]
                for t in bezier_clip_roots(dv):
                    bx, by = eval_segment(P, t)
                    s = ux * (float(bx) - ox) + uy * (float(by) - oy)
                    if s <= 0:
                        continue
                    tan = deriv_segment(P, t)
                    field[r, c] += 1 if (nx * tan[0] + ny * tan[1]) > 0 else -1

    return field / n_rays
