# Academic Page — Claude Notes

## Blog posts

Posts live in `_posts/` as Markdown files. The blog listing page is `_pages/blog.html`.

Figures in posts are referenced with:
```liquid
<div class="text-center">
{% include figure.liquid path="assets/img/blog/<post-slug>/figN_name.svg" class="img-fluid rounded z-depth-1" max-width="300px" %}
</div>
```
Always set `max-width` (without it the SVG stretches to full column width) and wrap in `text-center` to center it.

## Figure generation

All figure scripts live in `scripts/figures/`. Generated assets go to `assets/img/blog/<post-slug>/`.

**Run a figure:**
```bash
.venv/bin/python scripts/figures/figN_name.py
```

**Format:** SVG only — no PNGs. Vector output scales without loss.

**Consistency rules** — every figure must follow these:
- Import and use `COLORS`, `setup_ax`, and `save_fig` from `scripts/figures/utils.py`
- Use `utils.py` color palette for all visual elements (polygons, points, rays, etc.) — do not introduce ad-hoc colors
- Call `setup_ax(ax)` to get a uniform no-axis, white-background style
- Set `figsize` per figure to match the content's natural aspect ratio; aim for roughly half the matplotlib default (i.e. ~3×3 inches)
- Set `ax.set_xlim` / `ax.set_ylim` tightly around the actual content with minimal padding (~0.2–0.3 units) — no excess whitespace above or below
- Keep `linewidth=2.0` for polygon edges throughout

**Adding a new color role:** add it to `COLORS` in `utils.py` first, then use it by key in figure scripts.
