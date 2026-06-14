(function () {
  'use strict';

  // ── Cubic solver ────────────────────────────────────────────────────────────

  function solveQuadratic(a, b, c) {
    if (Math.abs(a) < 1e-12) {
      if (Math.abs(b) < 1e-12) return [];
      return [-c / b];
    }
    const disc = b * b - 4 * a * c;
    if (disc < 0) return [];
    if (disc < 1e-12) return [-b / (2 * a)];
    const sq = Math.sqrt(disc);
    return [(-b - sq) / (2 * a), (-b + sq) / (2 * a)];
  }

  function solveCubic(a, b, c, d) {
    if (Math.abs(a) < 1e-12) return solveQuadratic(b, c, d);

    const A = b / a, B = c / a, C = d / a;
    const p = B - A * A / 3;
    const q = 2 * A * A * A / 27 - A * B / 3 + C;
    const D = p * p * p / 27 + q * q / 4;

    const shift = -A / 3;

    if (D < -1e-14) {
      // Three distinct real roots — trigonometric method
      const r = Math.sqrt(-p * p * p / 27);
      const phi = Math.acos(Math.max(-1, Math.min(1, -q / (2 * r))));
      const m = 2 * Math.cbrt(r);
      return [
        m * Math.cos(phi / 3) + shift,
        m * Math.cos((phi + 2 * Math.PI) / 3) + shift,
        m * Math.cos((phi + 4 * Math.PI) / 3) + shift,
      ];
    }

    // One real root (or repeated) — Cardano
    const sqrtD = Math.sqrt(Math.max(0, D));
    const u = Math.cbrt(-q / 2 + sqrtD);
    const v = Math.cbrt(-q / 2 - sqrtD);
    const roots = [u + v + shift];
    if (D < 1e-14) roots.push(-(u + v) / 2 + shift); // repeated root
    return roots;
  }

  // ── Bézier helpers ──────────────────────────────────────────────────────────

  function bx(t, P) {
    const mt = 1 - t;
    return mt*mt*mt*P[0].x + 3*mt*mt*t*P[1].x + 3*mt*t*t*P[2].x + t*t*t*P[3].x;
  }

  function dyt(t, c1, c2, c3) {
    return c1 + 2 * c2 * t + 3 * c3 * t * t;
  }

  // ── GWN (one-shot method) ───────────────────────────────────────────────────

  function computeGWN(px, py, P) {
    const TAU = 2 * Math.PI;

    // Polynomial coefficients for B(t).y - py = 0
    const a0 = P[0].y - py, a1 = P[1].y - py, a2 = P[2].y - py, a3 = P[3].y - py;
    const c0 = a0;
    const c1 = 3 * (a1 - a0);
    const c2 = 3 * (a0 - 2 * a1 + a2);
    const c3 = -a0 + 3 * a1 - 3 * a2 + a3;

    // Signed crossings with +x ray
    const roots = solveCubic(c3, c2, c1, c0);
    let chi = 0;
    for (const t of roots) {
      if (t >= 0 && t <= 1) {
        const x = bx(t, P);
        if (x > px) {
          const dy = dyt(t, c1, c2, c3);
          if (Math.abs(dy) > 1e-10) chi += dy > 0 ? 1 : -1;
        }
      }
    }

    // Angles to endpoints
    const as = Math.atan2(P[0].y - py, P[0].x - px);
    const ae = Math.atan2(P[3].y - py, P[3].x - px);

    // θ1 = size of CCW arc from ae → as
    const theta1 = ((as - ae) % TAU + TAU) % TAU;

    // Is the +x ray (angle 0) in arc1?
    const phi = ((-ae) % TAU + TAU) % TAU;
    const inArc1 = phi < theta1;

    return chi + (inArc1 ? 1 : 0) - theta1 / TAU;
  }

  // ── Color map ────────────────────────────────────────────────────────────────

  function gwnToRGB(gwn) {
    const t = Math.max(-1, Math.min(1, gwn / 1.5));
    if (t >= 0) {
      return [255, Math.round(255 * (1 - t)), Math.round(255 * (1 - t))];
    } else {
      return [Math.round(255 * (1 + t)), Math.round(255 * (1 + t)), 255];
    }
  }

  // ── Applet class ─────────────────────────────────────────────────────────────

  class GWNBezierApplet {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');

      // Logical size — we use CSS to scale
      const size = 420;
      canvas.width = size;
      canvas.height = size;
      this.size = size;

      // Offscreen canvas for the field
      this.field = document.createElement('canvas');
      this.field.width = 256;
      this.field.height = 256;
      this.fctx = this.field.getContext('2d');

      // Control points stored as fractions [0,1]
      this.pts = [
        { x: 0.15, y: 0.28 },
        { x: 0.15, y: 0.72 },
        { x: 0.85, y: 0.28 },
        { x: 0.85, y: 0.72 },
      ];

      this.dragging = null;
      this.rafPending = false;

      canvas.addEventListener('pointerdown', this._onDown.bind(this));
      canvas.addEventListener('pointermove', this._onMove.bind(this));
      canvas.addEventListener('pointerup', this._onUp.bind(this));
      canvas.addEventListener('pointercancel', this._onUp.bind(this));

      this._render();
    }

    // Convert fraction coords → pixel coords
    _px(pt) {
      return { x: pt.x * this.size, y: pt.y * this.size };
    }

    _renderField() {
      const W = this.field.width, H = this.field.height;
      const img = this.fctx.createImageData(W, H);
      const data = img.data;
      const P = this.pts.map(p => ({ x: p.x * this.size, y: p.y * this.size }));

      for (let row = 0; row < H; row++) {
        for (let col = 0; col < W; col++) {
          const px = (col + 0.5) / W * this.size;
          const py = (row + 0.5) / H * this.size;
          const gwn = computeGWN(px, py, P);
          const [r, g, b] = gwnToRGB(gwn);
          const i = (row * W + col) * 4;
          data[i] = r; data[i+1] = g; data[i+2] = b; data[i+3] = 255;
        }
      }
      this.fctx.putImageData(img, 0, 0);
    }

    _drawScene() {
      const ctx = this.ctx;
      const S = this.size;
      const pts = this.pts.map(p => ({ x: p.x * S, y: p.y * S }));

      ctx.clearRect(0, 0, S, S);

      // Field background
      ctx.drawImage(this.field, 0, 0, S, S);

      const [P0, P1, P2, P3] = pts;

      // Control polygon
      ctx.save();
      ctx.setLineDash([5, 5]);
      ctx.strokeStyle = 'rgba(0,0,0,0.3)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(P0.x, P0.y);
      ctx.lineTo(P1.x, P1.y);
      ctx.lineTo(P2.x, P2.y);
      ctx.lineTo(P3.x, P3.y);
      ctx.stroke();
      ctx.restore();

      // Bézier curve
      ctx.save();
      ctx.strokeStyle = '#111';
      ctx.lineWidth = 2.5;
      ctx.lineJoin = 'round';
      ctx.beginPath();
      ctx.moveTo(P0.x, P0.y);
      ctx.bezierCurveTo(P1.x, P1.y, P2.x, P2.y, P3.x, P3.y);
      ctx.stroke();
      ctx.restore();

      // Arrowhead at t = 0.65
      this._drawArrow(pts, 0.65);

      // Control handles
      const ENDPOINT_FILL = '#111';
      const HANDLE_FILL = '#fff';
      pts.forEach((pt, i) => {
        const isEndpoint = i === 0 || i === 3;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = isEndpoint ? ENDPOINT_FILL : HANDLE_FILL;
        ctx.fill();
        ctx.strokeStyle = '#111';
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    }

    _drawArrow(pts, t) {
      const [P0, P1, P2, P3] = pts;
      const mt = 1 - t;

      // Point on curve
      const ax = mt*mt*mt*P0.x + 3*mt*mt*t*P1.x + 3*mt*t*t*P2.x + t*t*t*P3.x;
      const ay = mt*mt*mt*P0.y + 3*mt*mt*t*P1.y + 3*mt*t*t*P2.y + t*t*t*P3.y;

      // Tangent direction
      const dx = 3*mt*mt*(P1.x-P0.x) + 6*mt*t*(P2.x-P1.x) + 3*t*t*(P3.x-P2.x);
      const dy = 3*mt*mt*(P1.y-P0.y) + 6*mt*t*(P2.y-P1.y) + 3*t*t*(P3.y-P2.y);
      const len = Math.sqrt(dx*dx + dy*dy);
      if (len < 1e-6) return;

      const ux = dx / len, uy = dy / len;
      const size = 11;

      const ctx = this.ctx;
      ctx.save();
      ctx.fillStyle = '#111';
      ctx.beginPath();
      ctx.moveTo(ax + ux * size, ay + uy * size);
      ctx.lineTo(ax - ux * size * 0.5 - uy * size * 0.6, ay - uy * size * 0.5 + ux * size * 0.6);
      ctx.lineTo(ax - ux * size * 0.5 + uy * size * 0.6, ay - uy * size * 0.5 - ux * size * 0.6);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    _render() {
      this._renderField();
      this._drawScene();
      this.rafPending = false;
    }

    _scheduleRender() {
      if (this.rafPending) return;
      this.rafPending = true;
      requestAnimationFrame(() => this._render());
    }

    _getCanvasXY(e) {
      const rect = this.canvas.getBoundingClientRect();
      return {
        x: (e.clientX - rect.left) * (this.size / rect.width),
        y: (e.clientY - rect.top)  * (this.size / rect.height),
      };
    }

    _hitTest(x, y) {
      const S = this.size;
      let best = -1, bestDist = 28 * (this.size / this.canvas.getBoundingClientRect().width);
      this.pts.forEach((pt, i) => {
        const dx = pt.x * S - x, dy = pt.y * S - y;
        const d = Math.sqrt(dx*dx + dy*dy);
        if (d < bestDist) { bestDist = d; best = i; }
      });
      return best;
    }

    _onDown(e) {
      e.preventDefault();
      const { x, y } = this._getCanvasXY(e);
      const hit = this._hitTest(x, y);
      if (hit < 0) return;
      this.dragging = hit;
      this.canvas.setPointerCapture(e.pointerId);
      this.canvas.style.cursor = 'grabbing';
    }

    _onMove(e) {
      if (this.dragging === null) return;
      e.preventDefault();
      const { x, y } = this._getCanvasXY(e);
      const pad = 0.02;
      this.pts[this.dragging] = {
        x: Math.max(pad, Math.min(1 - pad, x / this.size)),
        y: Math.max(pad, Math.min(1 - pad, y / this.size)),
      };
      this._scheduleRender();
    }

    _onUp(e) {
      this.dragging = null;
      this.canvas.style.cursor = 'grab';
    }
  }

  // ── Auto-init ────────────────────────────────────────────────────────────────

  function init() {
    document.querySelectorAll('canvas[data-applet="gwn-bezier"]').forEach(canvas => {
      if (canvas.dataset.gwnInitialized) return;
      canvas.dataset.gwnInitialized = 'true';
      new GWNBezierApplet(canvas);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
