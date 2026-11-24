# Pending approved design decisions (proof stage — NOT yet built)

Tracking user-confirmed requirements relayed via main. Implement only after
explicit approval of the corresponding visual proofs.

## Desktop icons
- Icon set: 3dicons (CC0, https://github.com/realvjy/3dicons), isometric angle,
  gradient renders, recolored to the system accent (teal = full, sky blue #4fb2f7
  family = live) via luminance gradient-map that preserves the render shading.
- **My PC icon (set's "computer") is ALWAYS on the desktop in BOTH variants**
  (user confirmation 2026-11-24, "خليها دايما في النسختين على الـdesktop").
  Place it at the top of the desktop icon column, Windows-style.
- Missing-from-set icons (Home, Floppy/Save) get custom-drawn in the same look.
- Desktop icon columns per variant (top to bottom):
  - full: My PC, Home, File System, Trash, Floppy Disk, Install, Guide
  - live: My PC, Home, File System, Trash, Floppy Disk, Live Guide, Guide AR

## Taskbar (awaiting approval of proof13/proof10 glass look)
- Translucent colored glass bar per variant accent (teal full / sky blue live),
  top gloss + highlight line, wallpaper visible through; white text w/ shadow.
- Crescent orb button LEFT of middle (~36% width), straddling the top edge.
- Small credit pill attached top-right: "Directed by Mohamed Sayed · محمد سيد".
- No window buttons while nothing is open; Aero-style glass button per open app.
- Recolors live from the Theme Color tool (any wheel color).

## Taskbar updates (user feedback 2026-11-24, proof stage, NOT built)
- No white outline/edge lines on the bar or credit pill. No drop shadows anywhere
  (bar, credit pill, window buttons, crescent orb, desktop icons, labels, bar text).
- Crescent orb button IS outlined in white (only white line in the design).
- Real build renders curves fully smooth (anti-aliased, no pixelation); proofs show
  rasterization artifacts that will not exist in the real version.
- Clock shows AM/PM next to the time by time of day; switchable to Arabic (ص / م).
- Reflect the clock AM/PM in the next proof only after the user answers proof18.

## Theme Color follows icons and glass bar (approved 2026-11-24 5:26pm, "تمام يلا")
- On Apply in the Theme Color tool, icons and the glass taskbar are regenerated from the chosen color.
- Icons: grayscale master icons recolored with the luminance gradient-map pipeline (a few seconds).
- Glass bar: generated from the same color.
- Not built yet. Fold into the full design build once the design is approved. Needs one build plus a QEMU test.

## proof20 feedback (2026-11-24 5:29pm)
- Live wallpaper background: blue (sky blue hue shift of the teal sky; moon and stars unchanged). Full stays teal unless he says otherwise.
- Crescent orb ring (both versions): anti-aliased, muted white normally, bright glossy white with a soft glow when pressed.

## proof21/22 feedback (2026-11-24 5:36pm)
- Orange preset too harsh: replaced by soft orange #e8a05c (less saturated). Ice preset #9fdcf0 added as a test color.
- Crescent orb white ring slightly thicker in all versions (3px -> ~4.6px, anti-aliased).

## Approved (2026-11-24 5:37pm)
- Soft orange preset #e8a05c approved (proof22). Thicker anti-aliased crescent ring shown in proof22. Replaces #f28c28 in the Theme Color preset list.

## Wallpaper follows theme (2026-11-24 5:40pm)
- On Apply, the wallpaper sky is recolored from the chosen color (all 12 presets); moon fixed. Stars stay light.
- Defaults are unchanged: live default wallpaper = the approved deep blue (hue-shifted teal, proof20), full default = teal. The recolor applies only when a theme color is chosen. Do not use the proof24 lighter blue as the default.

## Credit line baseline (standing rule, 2026-11-24 5:41pm)
- "Directed by Mohamed Sayed · محمد سيد": draw both parts on the same baseline (anchor 'ls' at one y), Arabic in Noto Kufi Arabic Bold ~12px next to Comfortaa Bold 13px for matching visual weight. proof25.

- APPROVED by Mohamed 2026-11-24 5:42pm (proof25): credit line baseline fix with Noto Kufi Arabic Bold.

## Softer wallpapers: REVERTED (2026-11-24 5:44pm)
- Mohamed rejected the 35% desaturation (proof26). Theme wallpapers stay as in proof24 (no desaturation).

## Boot menu proof4 (2026-11-24 5:47pm)
- proof3 approved by Mohamed with one change: the bottom text (credit line, "Automatic boot...", "Press ENTER...") darker navy (#0a2642) for legibility, both versions. Credit line on one baseline (Noto Kufi Arabic Bold). Not applied to the real boot menu until proof4 is approved.

## Boot menu proof5 (2026-11-24 5:49pm)
- Bottom text smaller (21px -> 17px) and lighter medium blue (#1a4e74) than proof4 navy, still clearly visible. Real boot menu unchanged until approved.

## Boot menu proof5 APPROVED (2026-11-24 5:50pm, "تمام")
- Apply to the real boot menu (both versions): smaller bottom text, medium blue #1a4e74.

## Combined 64+32-bit ISO (approved by Mohamed 2026-11-24 5:54pm, 'تمام', incl. 32-bit browser caveat)
- One ISO: /live = 64-bit Debian 13, /live32 = 32-bit Debian 12 (bookworm) with the same design. Boot menu proof6 is the design reference (not yet commented on by him).
- Auto-select by CPU: syslinux ifcpu64.c32 (BIOS); GRUB cpuid -l (UEFI, 32-bit UEFI best effort).
- 32-bit caveats accepted: no supported Firefox on 32-bit Linux (ESR 140 ended 2026-09-29), Debian 12 LTS only, no Bottles (Flathub has no i386).

## Secure Browser icon (approved 2026-11-24 6:04 PM EET, user message "رقم ٣ اعتمده")
- Concept 3 of proof2: dark glass orb, real-moon crescent with soft glow, orbiting light-network (glowing metal-shaded nodes, thin orbit strands). Sky blue theme proof; recolors with Theme Color.
- Source: theme/browser/gen-browser-icon.py, master theme/browser/secure-browser-icon-512.png.
- TODO final: simplified variants for 32px and below (fewer nodes, no thin strands).
- Browser product name stays the placeholder "Secure Browser". Open: branded Firefox ESR/Chromium build (plan) vs real Brave on 64-bit.
