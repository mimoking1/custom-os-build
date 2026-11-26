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
- 3d-*.png: four 3D renders (lossless) generated for this project.
- No real photographs are shipped (all photo wallpapers were removed 2026-11-26 at the user's request). The gallery holds only the four in-house 3D renders.

## Android (optional)
Android support uses Waydroid (GPL-3.0), installed on demand from its own repository, vanilla image by default.
The "Android: add Google Play" menu item (customos-android gapps) is OFF by default: it only runs if the user clicks it and confirms a dialog
that says the Play stack downloads from Google's servers under Google's terms. No Google software is shipped in the ISO.

## Icon themes
- Arcanum (Blue), by StormRosenaa, GPL-3.0, https://codeberg.org/StormRosenaa/Arcanum. Default system icon theme (apps, file types, places). Fetched at ISO build time and pinned by sha256; it inherits Papirus-Dark for anything it lacks.
- Papirus (GPL-3.0) as fallback via Debian package papirus-icon-theme.
- 3dicons by realvjy (CC0), recolored: desktop icons only (customos-* names).
