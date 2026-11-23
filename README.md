# Custom OS — build repository

A customized, lightweight, Debian-based live/installer OS: modern simple desktop,
English default UI with Arabic ready out of the box, every language switchable in
Settings, Wine for Windows apps, and a free design suite preinstalled.

## The two versions
| Version | File | Purpose |
|---|---|---|
| Full | `customos-full-amd64.iso` | Live session **with** a graphical installer (Calamares) on the desktop |
| Live | `customos-live-amd64.iso` | Live-only: boots from USB, installs nothing, clearly labeled |

## Set the OS name
One line in `variants/full.conf` and `variants/live.conf` (`OS_NAME=`). The owner
picks the final name; everything (boot menu, installer branding, panel button)
takes it from there.

## Build (CI, recommended)
GitHub Actions → "Build and boot-test ISOs" → Run workflow → pick `full`, `live`
or `both`. Each run:
1. Installs live-build and builds the ISO (Debian trixie, XFCE).
2. Boots the ISO in QEMU/KVM and saves staged screenshots as proof it reaches
   the desktop (`boot-test/*.png` in the artifacts).
3. Uploads the ISO, SHA256SUMS, and the boot-test evidence as artifacts.
4. On a version tag (`v*`), attaches ISOs under 2 GiB to a GitHub Release.
   Bigger ISOs go to SourceForge / archive.org / Google Drive (see HOSTING below).

## Build (local Linux machine with root)
```
sudo ./build/build-iso.sh variants/full.conf
sudo ./build/build-iso.sh variants/live.conf
./build/boot-test/boot-test.sh out/customos-full-amd64.iso out/boot-test
```
Requires: Debian/Ubuntu host, ~20 GB free disk, KVM for the boot test.

## Repo layout
- `variants/` — per-version settings (name, installer yes/no, suite)
- `build/build-iso.sh` — the whole build: lb config, packages, theme, hooks
- `build/packages/` — what gets installed (desktop, apps, fonts, languages)
- `build/includes.chroot/` — files overlaid into the system: theme, panel,
  LightDM greeter, Photopea shortcut, language picker, .exe→Wine handler
- `build/hooks/` — chroot hooks (Wine/i386 install, desktop defaults, installer)
- `build/boot-test/` — QEMU/KVM boot test with screenshot evidence
- `theme/` — wallpapers and logo (source SVGs, rendered at build time)
- `installer/` — Calamares settings + branding (full variant only)
- `guide/GUIDE-AR.md` — the Arabic user guide (burn, boot, install, FAQ)

## Languages
Default UI: English. Arabic + English keyboard preconfigured (Super+Space or the
panel indicator). All other languages: Settings → "Language / اللغة" picks any
locale; UI packs download on demand (same model as Ubuntu), keeping the ISO lean.

## Honest limits
- Boot tests prove the ISO works in a virtual machine. Real-hardware drivers
  (WiFi/GPU) differ per device — test with the live USB first; it changes nothing.
- Wine runs many Windows apps, not all. Adobe apps are experimental (see guide).
- DaVinci Resolve can't be preinstalled (vendor download needs registration);
  Kdenlive is preinstalled and the guide shows how to add Resolve manually.

---
Directed by Mohamed Sayed · محمد سيد
