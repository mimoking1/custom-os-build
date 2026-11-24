#!/usr/bin/env python3
"""Render 24 frames of the crescent doing a slow 3D flip (rotate around vertical axis)."""
import math, os, sys
from PIL import Image, ImageEnhance

SRC = sys.argv[1] if len(sys.argv) > 1 else "theme/crescent-moon.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "build/plymouth/frames"
os.makedirs(OUT, exist_ok=True)
moon = Image.open(SRC).convert("RGBA")
# normalize to square canvas
side = max(moon.size)
sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
sq.paste(moon, ((side - moon.width) // 2, (side - moon.height) // 2), moon)
sq = sq.resize((280, 280), Image.LANCZOS)

N = 24
for i in range(N):
    theta = 2 * math.pi * i / N
    sx = abs(math.cos(theta))            # horizontal squeeze = flip around vertical axis
    sx = max(sx, 0.12)                   # never fully vanish edge-on
    w = max(1, int(280 * sx))
    frame = sq.resize((w, 280), Image.LANCZOS)
    # fake lighting: dim when edge-on, full when facing
    bright = 0.55 + 0.45 * abs(math.cos(theta))
    alpha = frame.getchannel("A").point(lambda a: int(a * min(1.0, bright + 0.25)))
    frame.putalpha(alpha)
    canvas = Image.new("RGBA", (280, 280), (0, 0, 0, 0))
    canvas.paste(frame, ((280 - w) // 2, 0), frame)
    canvas.save(os.path.join(OUT, "flip-%02d.png" % i))
print("frames written to", OUT)
