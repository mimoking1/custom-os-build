# Asset licenses

- Moon imagery: "Full Moon (5836482263)" by NASA, Public Domain.
  Source: https://commons.wikimedia.org/wiki/File:Full_Moon_(5836482263).jpg
  Used in: crescent moon start button, boot splash, installer sidebar, night-sea wallpaper.
  Processed (cropped, crescent-masked, warm tint, soft glow) from the original public-domain image.
- All other artwork (wallpapers, icons, logo, patterns): original work for this project, free to use.

## Wallpapers (theme/wallpaper/*.svg)
All wallpaper artwork is ORIGINAL, generated in-house for this project (2026-11-24):
layered wave gradients built from the user's chosen color swatch #08e8de
(supplied by the user as an image; hex measured from its pixels).
No Vecteezy or other stock assets are used: Vecteezy's free license requires
attribution and forbids redistributing content as standalone assets, which is
incompatible with shipping files in this public repo and the ISO.
- wallpaper-allahu-akbar.svg, wallpaper-waves.svg, wallpaper-geometry.svg,
  wallpaper-nature-dunes.svg: original vector waves/stars/dunes.
- wallpaper-night-sea.svg: original waves + the public-domain NASA moon photo
  (see Crescent moon above) + stars.
License for all of the above: released with this repo (MIT, same as build scripts).

## Fonts used for calligraphy
- Amiri (الله أكبر wallpaper rendering): SIL Open Font License 1.1,
  (c) The Amiri Project Authors, https://github.com/aliftype/amiri
  Shipped on the ISO via Debian package fonts-hosny-amiri.
- Aref Ruqaa, Reem Kufi (alternative renderings, previews only): SIL OFL 1.1.

## pngtree
The Islamic-wallpaper reference page the user sent (ar.pngtree.com) was NOT used:
pngtree's free license is personal/non-profit only, requires an account and
attribution, and forbids redistribution. wallpaper-islamic-skyline.svg is an
ORIGINAL design (mosque skyline silhouette + gold crescent over the aqua waves)
made in the same spirit.

## Fonts
- Comfortaa (rounded display font, boot artwork title): SIL Open Font License 1.1, https://github.com/googlefonts/comfortaa

## Wallpaper gallery (build/includes.chroot/usr/share/backgrounds/customos/gallery)
- 3d-*.png (4) and 3d-*.jpg (6 Blender renders): generated for this project, ours.
- 16 photographs, added 2026-11-26 at the user's explicit request and approval. They are NOT in this
  public repo. The build fetches them from a private release and ships them inside the ISO only.
  Source: Pexels, free licence https://www.pexels.com/license/ (no attribution required; no resale or
  redistribution as stock/wallpaper packs; kept out of the public repo for that reason).
  Pexels photo IDs: Mecca 11895059, 34246982, 40483736; Madinah 38498727, 27628044, 35241863;
  Jerusalem 11696756, 26615654, 17814827; horses 14704404, 18169927, 18169954, 40155303, 37786209,
  26712207; Quran (open Quran, green and gold binding) 20784677. Cropped to 3840x2160 (16:9) only.
