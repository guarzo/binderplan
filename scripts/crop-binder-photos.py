#!/usr/bin/env python
"""Detect the card-bearing region of a binder photo and crop to it.

The backdrops are flat: black binder fabric, or the beige wall behind it. Cards
are not, so the detector works in three stages:

  1. seed    - local gradient energy or saturation. Finds card art and print, but
               on a divider card only the text block, since the card is flat.
  2. fill    - close enclosed holes. A divider card seeds only its text and its
               outline; filling the gap between them recovers the whole card.
               The wall touches the frame border, so it is never enclosed.
  3. bridge  - dilate, then keep the connected region richest in seed. Closes the
               gutters between pockets so a page reads as one region, while a
               zipper strip or lone index tab drops out.

Usage:
    pip install pillow numpy
    python scripts/crop-binder-photos.py OUTDIR photo.webp [photo2.webp ...]

Handles both full 9-pocket pages and a lone divider card on an empty page. Prints
how much of each frame survived; anything near 100% means nothing was found to
trim, and anything under ~30% is worth eyeballing before you publish it.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

WORK_W = 700          # analysis resolution
BLOCK = 4             # grid cell size for connectivity work
BLUR = 4              # box-blur radius; small enough that a thin card edge survives
GRAD_T = 0.040        # gradient energy that reads as content
SAT_T = 0.22          # saturation that reads as card art
GROW = 5              # gutter-bridging dilation, in grid cells
MIN_DIM = 0.12        # a region thinner than this on either axis is binder hardware
MIN_FILL = 0.55       # cards fill their bounding box; the zipper band does not
PROJ_T = 0.14         # keep rows/cols holding >= this fraction of peak mass
PAD = 0.012           # padding as a fraction of the long edge


def box_blur(a, r):
    """Separable box blur via a summed-area table."""
    for _ in range(2):  # twice, for a smoother gaussian-ish falloff
        c = np.cumsum(np.pad(a, ((r + 1, r), (0, 0)), mode="edge"), axis=0)
        a = ((c[2 * r + 1:] - c[:-(2 * r + 1)]) / (2 * r + 1)).T
    return a


def dilate(m):
    out = m.copy()
    out[1:] |= m[:-1]; out[:-1] |= m[1:]
    out[:, 1:] |= m[:, :-1]; out[:, :-1] |= m[:, 1:]
    return out


def to_grid(mask, cover=0.3):
    bh, bw = mask.shape[0] // BLOCK, mask.shape[1] // BLOCK
    cells = mask[:bh * BLOCK, :bw * BLOCK].reshape(bh, BLOCK, bw, BLOCK)
    return cells.mean(axis=(1, 3)) > cover


def cues(rgb):
    g = rgb.mean(axis=2)
    gx = np.abs(np.diff(g, axis=1, prepend=g[:, :1]))
    gy = np.abs(np.diff(g, axis=0, prepend=g[:1, :]))
    grad = box_blur(gx + gy, BLUR)

    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = box_blur(np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0.0), BLUR)

    return to_grid((grad > GRAD_T) | (sat > SAT_T))


def fill_holes(seed):
    """Close regions of `seed` that enclose flat interiors.

    A divider card seeds only its printed text plus its own outline against the
    dark binder; the blank interior between them is an enclosed hole. Filling it
    recovers the whole card. Deliberately not a brightness fill: the wall is
    bright too, and the binder's textured seam touches it, so brightness would
    leak the backdrop into the region. A hole cannot leak - anything continuous
    with the frame border is by definition not enclosed.
    """
    outside = np.zeros_like(seed)
    outside[0, :] = outside[-1, :] = True
    outside[:, 0] = outside[:, -1] = True
    outside &= ~seed
    for _ in range(sum(seed.shape)):
        nxt = dilate(outside) & ~seed
        if np.array_equal(nxt, outside):
            break
        outside = nxt
    return seed | ~(outside | seed)


def best_region(content, seed):
    """The connected region of `content` holding the most `seed`, gutters closed."""
    grown = content.copy()
    for _ in range(GROW):
        grown = dilate(grown)

    seen = np.zeros_like(grown)
    best = None
    for sy, sx in zip(*np.nonzero(grown)):
        if seen[sy, sx]:
            continue
        stack, cells = [(sy, sx)], []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < grown.shape[0] and 0 <= nx < grown.shape[1] \
                        and grown[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))
        # Rank by seed mass, but only among plausibly card-shaped regions. The
        # binder's zipper and top seam are richly textured and can outscore a
        # lone divider card on mass alone. Cards - single or a full page with the
        # gutters closed - fill their bounding box; the zipper is a sparse
        # diagonal band that fills well under half of its own.
        ys, xs = [c[0] for c in cells], [c[1] for c in cells]
        bh = max(ys) - min(ys) + 1
        bw = max(xs) - min(xs) + 1
        density = len(cells) / (bh * bw)
        boxy = min(bh / grown.shape[0], bw / grown.shape[1]) >= MIN_DIM
        mass = sum(seed[y, x] for y, x in cells)
        rank = (boxy and density >= MIN_FILL, mass)
        if best is None or rank > best[0]:
            best = (rank, cells)

    keep = np.zeros_like(content)
    for y, x in best[1]:
        keep[y, x] = True
    return content & keep


def span(proj):
    """Outermost extent above PROJ_T of peak.

    Deliberately not the largest contiguous run: the gutters between pockets drop
    the projection to near zero, which would yield a single column of cards.
    """
    hits = np.flatnonzero(proj >= PROJ_T * proj.max())
    return (hits[0], hits[-1] + 1) if hits.size else (0, len(proj))


def crop_box(path):
    im = Image.open(path).convert("RGB")
    W, H = im.size
    small = im.resize((WORK_W, max(1, round(H * WORK_W / W))), Image.BILINEAR)
    rgb = np.asarray(small, dtype=np.float32) / 255.0

    seed = cues(rgb)
    region = best_region(fill_holes(seed), seed)
    x0, x1 = span(region.sum(axis=0).astype(np.float32))
    y0, y1 = span(region.sum(axis=1).astype(np.float32))

    s = W / small.width * BLOCK  # grid cells -> full-resolution pixels
    pad = PAD * max(W, H)
    return (
        max(0, round(x0 * s - pad)), max(0, round(y0 * s - pad)),
        min(W, round(x1 * s + pad)), min(H, round(y1 * s + pad)),
    ), im


def main(outdir, paths):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for p in map(Path, paths):
        box, im = crop_box(p)
        out = im.crop(box)
        out.save(outdir / f"{p.stem}.webp", quality=88, method=5)
        pct = 100 * out.size[0] * out.size[1] / (im.size[0] * im.size[1])
        print(f"{p.name}: {im.size} -> {out.size}  ({pct:.0f}% kept)  box={box}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
