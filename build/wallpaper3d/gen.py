#!/usr/bin/env python3
"""Generate a 3D-look wallpaper: perspective arch corridor receding to a vanishing
point, glowing real-moon crescent, depth haze. Writes bg PNG + SVG wrapper (credit
text rendered by rsvg for correct Arabic shaping)."""
import base64, io, math, os, sys
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
OUTDIR = sys.argv[1]
MOON = sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
top, mid, bot = (4, 46, 43), (7, 110, 104), (8, 178, 170)
for y in range(H):
    t = y / H
    c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, bot, (t - 0.5) * 2)
    d.line([(0, y), (W, y)], fill=c)

VX, VY = 960, 560   # vanishing point

# 8-point stars, smaller and dimmer toward the horizon
def star8(cx, cy, r, rot=0.0):
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.42
        a = rot + math.pi * k / 8
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stars)
import random
random.seed(7)
for i in range(46):
    x = random.uniform(40, W - 40)
    y = random.uniform(30, VY - 20)
    depth = y / VY
    r = 7 + 26 * depth
    alpha = int(28 + 60 * depth)
    sd.polygon(star8(x, y, r, random.uniform(0, math.pi)), fill=(255, 255, 255, alpha))
img = Image.alpha_composite(img.convert("RGBA"), stars)

# receding arches: perspective corridor toward the vanishing point
arch = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ad = ImageDraw.Draw(arch)
NARCH = 6
for i in range(NARCH):
    t = i / (NARCH - 1)                    # 0 = nearest, 1 = farthest
    scale = 1.0 - 0.80 * t
    half_w = 820 * scale
    apex_y = VY - 430 * scale
    base_y = VY + 330 * scale
    col_top_y = apex_y + (base_y - apex_y) * 0.30
    shade = 1.0 - 0.5 * t
    gold = (int(212 * shade), int(175 * shade), int(55 * shade), 235)
    width = max(2, int(13 * scale))

    def arch_side(sign):
        # circle center on the opposite side so the arc curves inward to the apex
        cx = VX + sign * half_w * 0.45
        cy = apex_y + half_w * 0.95
        r = math.hypot(VX - cx, apex_y - cy)
        col = (VX - sign * half_w, col_top_y)
        a_apex = math.degrees(math.atan2(apex_y - cy, VX - cx)) % 360
        a_col = math.degrees(math.atan2(col[1] - cy, col[0] - cx)) % 360
        start, end = (a_apex, a_col) if a_col > a_apex else (a_col, a_apex)
        ad.arc([cx - r, cy - r, cx + r, cy + r], start, end, fill=gold, width=width)

    arch_side(+1)  # left half of the arch
    arch_side(-1)  # right half
    for sign in (+1, -1):
        x = VX - sign * half_w
        ad.line([(x, col_top_y), (x, base_y)], fill=gold, width=width)
    ad.line([(VX - half_w, base_y), (VX + half_w, base_y)], fill=gold, width=max(2, width // 2))

# soft depth haze near the horizon
haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(haze)
for y in range(H):
    t = max(0.0, 1.0 - abs(y - VY) / 380.0)
    hd.line([(0, y), (W, y)], fill=(8, 130, 122, int(70 * t * t)))
haze = haze.filter(ImageFilter.GaussianBlur(30))
img = Image.alpha_composite(img, arch)
img = Image.alpha_composite(img, haze)

# floor perspective lines
floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fd = ImageDraw.Draw(floor)
for k in range(-8, 9):
    fd.line([(VX, VY), (VX + k * 260, H)], fill=(4, 60, 56, 110), width=2)
for j in range(1, 9):
    y = VY + (H - VY) * (j / 9) ** 1.9
    fd.line([(0, y), (W, y)], fill=(4, 60, 56, 90), width=2)
img = Image.alpha_composite(img, floor)

# glowing crescent above the vanishing point
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
cx, cy, R = 960, 265, 150
for rr, a in [(R * 2.6, 26), (R * 2.0, 40), (R * 1.6, 60), (R * 1.3, 85)]:
    gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(120, 240, 228, a))
img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(18)))
moon = Image.open(MOON).convert("RGBA")
side = int(R * 2.0)
moon_sq = Image.new("RGBA", (max(moon.size),) * 2, (0, 0, 0, 0))
moon_sq.paste(moon, ((moon_sq.width - moon.width) // 2, (moon_sq.height - moon.height) // 2), moon)
moon_sq = moon_sq.resize((side, side), Image.LANCZOS)
img.alpha_composite(moon_sq, (cx - side // 2, cy - side // 2))

png_path = os.path.join(OUTDIR, "horizon3d-base.png")
img.convert("RGB").save(png_path, "PNG")

b64 = base64.b64encode(open(png_path, "rb").read()).decode()
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n'
       '<image x="0" y="0" width="1920" height="1080" href="data:image/png;base64,%s"/>\n'
       '<text x="960" y="988" text-anchor="middle" font-family="Amiri, Noto Sans Arabic, sans-serif" font-size="22" fill="#eafefc" opacity="0.92">Directed by Mohamed Sayed &#183; &#1605;&#1581;&#1605;&#1583; &#1587;&#1610;&#1583;</text>\n'
       '</svg>\n') % b64
open(os.path.join(OUTDIR, "wallpaper-horizon3d.svg"), "w").write(svg)
print("horizon3d generated:", png_path)
