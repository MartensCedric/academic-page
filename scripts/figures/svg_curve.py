"""Load the fig7 demo curve (and its query point) from an editable SVG.

The curve lives in ``curve_source.svg`` as a single ``<path>`` and the query point
as a ``<circle id="query">``. Edit that file in any vector editor (Inkscape,
Illustrator, ...) and re-run the fig7 scripts to regenerate the figures.

SVG space is y-down; we map it to math space (y-up) with a fixed affine transform
so what you see in the editor matches the figures:

    svg_x = x * SCALE + OX        x = (svg_x - OX) / SCALE
    svg_y = -y * SCALE + OY       y = -(svg_y - OY) / SCALE

The path is parsed into the same representation bezier.py uses: a list of cubic
segments, each a (4, 2) array of control points. M/L/H/V/C/S/Q/T/Z, absolute and
relative, are all supported (lines and quadratics are elevated to cubics).
"""
import os, re
import numpy as np
from xml.etree import ElementTree as ET

SCALE = 100.0
OX = 250.0
OY = 160.0

DEFAULT_SVG = os.path.join(os.path.dirname(__file__), "curve_source.svg")

_NUM = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
_CMD = re.compile(r"[MmLlHhVvCcSsQqTtZz]")


def to_math(sx, sy):
    return ((sx - OX) / SCALE, -(sy - OY) / SCALE)


def to_svg(x, y):
    return (x * SCALE + OX, -y * SCALE + OY)


def _tokenize(d):
    """Yield (command_letter, [floats]) groups from a path ``d`` string."""
    i = 0
    out = []
    for m in _CMD.finditer(d):
        out.append((m.start(), m.group()))
    for k, (pos, cmd) in enumerate(out):
        end = out[k + 1][0] if k + 1 < len(out) else len(d)
        nums = [float(x) for x in _NUM.findall(d[pos + 1:end])]
        yield cmd, nums


def _path_to_cubics(d):
    """Parse an SVG path ``d`` into a list of cubic segments in **svg** space."""
    segs = []
    cur = np.array([0.0, 0.0])
    start = np.array([0.0, 0.0])
    prev_cmd = None
    prev_ctrl = None  # second control point of last C/S (for S/T smoothing)

    def cubic(p0, p1, p2, p3):
        segs.append(np.array([p0, p1, p2, p3], dtype=float))

    for cmd, n in _tokenize(d):
        rel = cmd.islower()
        c = cmd.upper()
        idx = 0
        if c == "M":
            # first pair is moveto, subsequent pairs are implicit linetos
            x, y = n[idx], n[idx + 1]; idx += 2
            cur = (cur + [x, y]) if rel else np.array([x, y])
            start = cur.copy()
            while idx + 1 < len(n):
                x, y = n[idx], n[idx + 1]; idx += 2
                nxt = (cur + [x, y]) if rel else np.array([x, y])
                cubic(cur, cur + (nxt - cur) / 3, cur + 2 * (nxt - cur) / 3, nxt)
                cur = nxt
            prev_ctrl = None
        elif c in "LHV":
            while idx < len(n):
                if c == "L":
                    x, y = n[idx], n[idx + 1]; idx += 2
                    nxt = (cur + [x, y]) if rel else np.array([x, y])
                elif c == "H":
                    x = n[idx]; idx += 1
                    nxt = np.array([cur[0] + x, cur[1]]) if rel else np.array([x, cur[1]])
                else:  # V
                    y = n[idx]; idx += 1
                    nxt = np.array([cur[0], cur[1] + y]) if rel else np.array([cur[0], y])
                cubic(cur, cur + (nxt - cur) / 3, cur + 2 * (nxt - cur) / 3, nxt)
                cur = nxt
            prev_ctrl = None
        elif c == "C":
            while idx + 5 < len(n):
                pts = n[idx:idx + 6]; idx += 6
                if rel:
                    p1 = cur + pts[0:2]; p2 = cur + pts[2:4]; p3 = cur + pts[4:6]
                else:
                    p1 = np.array(pts[0:2]); p2 = np.array(pts[2:4]); p3 = np.array(pts[4:6])
                cubic(cur, p1, p2, p3); cur = p3; prev_ctrl = p2
        elif c == "S":
            while idx + 3 < len(n):
                pts = n[idx:idx + 4]; idx += 4
                if rel:
                    p2 = cur + pts[0:2]; p3 = cur + pts[2:4]
                else:
                    p2 = np.array(pts[0:2]); p3 = np.array(pts[2:4])
                p1 = 2 * cur - prev_ctrl if prev_cmd in ("C", "S") and prev_ctrl is not None else cur
                cubic(cur, p1, p2, p3); cur = p3; prev_ctrl = p2
        elif c == "Q":
            while idx + 3 < len(n):
                pts = n[idx:idx + 4]; idx += 4
                qc = (cur + pts[0:2]) if rel else np.array(pts[0:2])
                p3 = (cur + pts[2:4]) if rel else np.array(pts[2:4])
                cubic(cur, cur + 2 / 3 * (qc - cur), p3 + 2 / 3 * (qc - p3), p3)
                cur = p3; prev_ctrl = qc
        elif c == "T":
            while idx + 1 < len(n):
                p3 = (cur + n[idx:idx + 2]) if rel else np.array(n[idx:idx + 2]); idx += 2
                qc = 2 * cur - prev_ctrl if prev_cmd in ("Q", "T") and prev_ctrl is not None else cur
                cubic(cur, cur + 2 / 3 * (qc - cur), p3 + 2 / 3 * (qc - p3), p3)
                cur = p3; prev_ctrl = qc
        elif c == "Z":
            if not np.allclose(cur, start):
                cubic(cur, cur + (start - cur) / 3, cur + 2 * (start - cur) / 3, start)
            cur = start.copy(); prev_ctrl = None
        prev_cmd = c
    return segs


def load_curve(svg_path=DEFAULT_SVG):
    """Return ``(segments, query_point)`` in math space from the source SVG."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {"svg": root.tag.split("}")[0].strip("{")} if "}" in root.tag else {}

    def find(tag):
        return root.iter("{%s}%s" % (ns["svg"], tag)) if ns else root.iter(tag)

    d = None
    for p in find("path"):
        d = p.get("d"); break
    if d is None:
        raise ValueError(f"no <path> found in {svg_path}")
    svg_segs = _path_to_cubics(d)
    segs = [np.array([to_math(*pt) for pt in s]) for s in svg_segs]

    query = None
    for circ in find("circle"):
        cx, cy = float(circ.get("cx")), float(circ.get("cy"))
        query = to_math(cx, cy)
        break
    return segs, query
