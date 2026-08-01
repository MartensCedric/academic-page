"""Build the site favicon from the One-Shot method figure.

Crops the A1 sphere out of the One-Shot publication preview and writes the
square icon sizes referenced by _includes/head.liquid, plus a root favicon.ico.

Run with:
    .venv/bin/python scripts/make_favicon.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets/img/publication_preview/1s_wn_preview.png"
IMG_DIR = ROOT / "assets/img"

# Bounding box of the A1 sphere inside the 381x328 source, measured by
# thresholding the beige fill against the background: left, top, right, bottom.
DISC_BOX = (26, 67, 166, 207)

BACKGROUND = (255, 254, 246)
# Matches the black line art in the figure, softened so it does not overpower
# the sphere at 16px.
RIM_COLOR = (74, 64, 56)
RIM_FRACTION = 0.025  # rim width as a fraction of the icon size

# Rendered at 4x then downsampled, so the rim stays smooth at every size.
SUPERSAMPLE = 4

PNG_SIZES = {
    "favicon-512.png": 512,
    "favicon-192.png": 192,
    "favicon-48.png": 48,
    "apple-touch-icon.png": 180,
}
ICO_SIZES = [16, 32, 48]


def build_icon(size):
    """Return a square RGB icon of the sphere at `size` pixels, with a rim."""
    hi = size * SUPERSAMPLE
    disc = Image.open(SOURCE).convert("RGB").crop(DISC_BOX).resize((hi, hi), Image.LANCZOS)

    # The crop is tight to the sphere, so a full-frame circle is the sphere's
    # own outline. Masking to it drops the dashed leader lines and the slivers
    # of the surface patch that overhang the edge in the source figure.
    mask = Image.new("L", (hi, hi), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, hi - 1, hi - 1), fill=255)

    icon = Image.new("RGB", (hi, hi), BACKGROUND)
    icon.paste(disc, (0, 0), mask)

    rim = max(1, round(hi * RIM_FRACTION))
    inset = rim / 2
    ImageDraw.Draw(icon).ellipse(
        (inset, inset, hi - 1 - inset, hi - 1 - inset), outline=RIM_COLOR, width=rim
    )

    return icon.resize((size, size), Image.LANCZOS)


def main():
    for name, size in PNG_SIZES.items():
        path = IMG_DIR / name
        build_icon(size).save(path)
        print(f"wrote {path.relative_to(ROOT)} ({size}x{size})")

    # Google falls back to /favicon.ico and browsers request it unprompted, so
    # the multi-resolution .ico lives at the site root rather than in assets.
    ico_path = ROOT / "favicon.ico"
    largest = build_icon(max(ICO_SIZES))
    largest.save(ico_path, sizes=[(s, s) for s in ICO_SIZES])
    print(f"wrote {ico_path.relative_to(ROOT)} ({', '.join(str(s) for s in ICO_SIZES)})")


if __name__ == "__main__":
    main()
