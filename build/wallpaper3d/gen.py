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

# realistic starfield: bright cores over a soft glow layer
glow_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
core_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd2 = ImageDraw.Draw(glow_l)
cd2 = ImageDraw.Draw(core_l)
import random
random.seed(7)
for i in range(750):
    x = random.uniform(20, W - 20)
    y = random.uniform(15, VY - 10)
    depth = 0.45 + 0.55 * (y / VY)
    r = random.uniform(0.6, 2.1) * depth
    bright = random.uniform(0.4, 1.0) * depth
    tone = random.choice([(255, 255, 255), (255, 255, 255), (226, 240, 255), (214, 250, 246)])
    if bright > 0.5:
        g = r * 3.0
        gd2.ellipse([x - g, y - g, x + g, y + g], fill=tone + (int(70 * bright),))
    cd2.ellipse([x - r, y - r, x + r, y + r], fill=tone + (int(255 * bright),))
    if bright > 0.85 and r > 1.2:
        L = r * 8
        cd2.line([(x - L, y), (x + L, y)], fill=tone + (int(110 * bright),), width=1)
        cd2.line([(x, y - L), (x, y + L)], fill=tone + (int(110 * bright),), width=1)
stars = Image.alpha_composite(glow_l.filter(ImageFilter.GaussianBlur(2.0)), core_l)
img = Image.alpha_composite(img.convert("RGBA"), stars)

# (arch corridor removed per user request)

# soft depth haze near the horizon
haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(haze)
for y in range(H):
    t = max(0.0, 1.0 - abs(y - VY) / 380.0)
    hd.line([(0, y), (W, y)], fill=(8, 130, 122, int(70 * t * t)))
haze = haze.filter(ImageFilter.GaussianBlur(30))
img = Image.alpha_composite(img, haze)


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

# real water floor: mirror the sky, smear vertically, darken, add ripples
from PIL import ImageEnhance
sky = img.crop((0, 0, W, VY)).transpose(Image.FLIP_TOP_BOTTOM)
refl_img = sky.resize((W, (H - VY) // 7), Image.BILINEAR).resize((W, H - VY), Image.BILINEAR)
refl_img = refl_img.filter(ImageFilter.GaussianBlur(4))
refl_img = ImageEnhance.Brightness(refl_img.convert("RGB")).enhance(0.5)
refl_img = ImageEnhance.Color(refl_img).enhance(0.75).convert("RGBA")
# water darkens toward the viewer
ramp = Image.new("L", (1, H - VY))
rp = ramp.load()
for y in range(H - VY):
    rp[0, y] = int(255 * (1.0 - 0.62 * (y / (H - VY))))
ramp = ramp.resize((W, H - VY))
dark = Image.new("RGBA", (W, H - VY), (2, 40, 38, 255))
refl_img = Image.composite(refl_img, dark, ramp)
# fade the reflection with depth: strong near horizon, darker near the bottom
mask = Image.new("L", (W, H - VY), 0)
md = ImageDraw.Draw(mask)
for y in range(H - VY):
    t = y / (H - VY)
    md.line([(0, y), (W, y)], fill=int(215 * (1 - 0.55 * t)))
img.paste(refl_img, (0, VY), Image.merge("RGBA", (*refl_img.split()[:3], mask.split()[0])) if False else refl_img.putalpha(mask) or refl_img)
# subtle ripple lines across the water
rip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
rd = ImageDraw.Draw(rip)
random.seed(11)
for i in range(90):
    y = VY + (H - VY) * (random.random() ** 1.6)
    t = (y - VY) / (H - VY)
    wseg = random.uniform(40, 220) * (0.3 + t)
    x = random.uniform(0, W - wseg)
    a = int(random.uniform(18, 60) * (0.4 + t))
    rd.line([(x, y), (x + wseg, y)], fill=(220, 255, 250, a), width=1)
img = Image.alpha_composite(img, rip.filter(ImageFilter.GaussianBlur(0.6)))
# soft luminous horizon line where sky meets water
hz = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(hz).line([(0, VY), (W, VY)], fill=(190, 255, 246, 120), width=2)
img = Image.alpha_composite(img, hz.filter(ImageFilter.GaussianBlur(2)))

png_path = os.path.join(OUTDIR, "horizon3d-base.png")
img.convert("RGB").save(png_path, "PNG")

b64 = base64.b64encode(open(png_path, "rb").read()).decode()
svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080">\n'
       '<image x="0" y="0" width="1920" height="1080" href="data:image/png;base64,%s"/>\n'
       '<text x="960" y="988" text-anchor="middle" font-family="Amiri, Noto Sans Arabic, sans-serif" font-size="22" fill="#eafefc" opacity="0.92">Directed by Mohamed Sayed &#183; &#1605;&#1581;&#1605;&#1583; &#1587;&#1610;&#1583;</text>\n'
       '</svg>\n') % b64
open(os.path.join(OUTDIR, "wallpaper-horizon3d.svg"), "w").write(svg)
print("horizon3d generated:", png_path)
