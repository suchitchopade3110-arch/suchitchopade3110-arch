#!/usr/bin/env python3
"""Turn a cut-out photo into the dot grid used by the hero card.

    python scripts/make_portrait.py [data/portrait-cutout.png]

Input: a PNG with a transparent background (any background remover works),
cropped to roughly 4:3 around head and shoulders.
Output: data/portrait.json, a list of [col, row, lightness 0-99] for every
cell that falls on the subject. render_cards.py draws it; this script is the
only one that needs extra packages (pip install pillow numpy).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
COLS = 78  # more columns = finer portrait, bigger SVG

src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "portrait-cutout.png"
im = Image.open(src).convert("RGBA")
alpha = im.getchannel("A")
grey = ImageOps.grayscale(im.convert("RGB"))
grey = ImageOps.autocontrast(grey, cutoff=1, mask=alpha.point(lambda a: 255 if a > 128 else 0))
grey = grey.filter(ImageFilter.GaussianBlur(im.width / COLS / 4))
L, A = np.asarray(grey) / 255.0, np.asarray(alpha) / 255.0

cell = im.width / COLS
rows = int(im.height / cell)
cells = []
for j in range(rows):
    for i in range(COLS):
        x = (i + (0.5 if j % 2 else 0)) * cell  # odd rows shift half a cell
        x0, x1, y0, y1 = int(x), int(min(im.width, x + cell)), int(j * cell), int((j + 1) * cell)
        if x1 <= x0 or A[y0:y1, x0:x1].mean() < 0.5:
            continue
        cells.append([i, j, min(99, round(float(L[y0:y1, x0:x1].mean()) * 100))])

out = ROOT / "data" / "portrait.json"
out.write_text(json.dumps({"cols": COLS, "rows": rows, "cells": cells}, separators=(",", ":")) + "\n")
print(f"{len(cells)} dots, {COLS}x{rows} grid -> {out.relative_to(ROOT)}")
