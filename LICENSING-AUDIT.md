# Licensing and hygiene audit

Scope: both editions (Siraj, Siraj Live), 64-bit only. Checked on real VM boots (package list from the
licence lab on c39703e; hygiene probe on 56c73ce; final selftests on the final build).

## Rights
- No activation, no licence checks, no forced updates. Automatic updates are disabled.
- No Brave, Chromium or Firefox. The only browser is hilali (ours, WebKitGTK, LGPL).
- Icon theme Arcanum Blue (GPL-3.0) theme-wide; Papirus (GPL-3.0) also shipped.
- Fonts: Amiri / Amiri Quran, Cairo, Comfortaa, Lato (SIL OFL 1.1); DejaVu, Liberation, Noto as packaged by Debian.
- Sounds: startup/shutdown/usb-plug/usb-unplug self-made, CC0.
- Gallery: 10 of ours; 16 Pexels photos (IDs in ASSETS-LICENSE.md), Pexels licence, kept out of the public repo.
- 3dicons CC0; NASA moon public domain.
- Wine 10 (LGPL), winetricks (LGPL), KDE Connect (GPL), adb (Apache-2.0), scrcpy v5.0.1 upstream release
  (Apache-2.0, pinned with sha256; not packaged in Debian 13). Tahmeel keeps its own name and is not redistributed publicly.
- Non-free firmware kept on purpose (firmware-*, intel/amd microcode, b43-fwcutter, alsa-firmware-loaders).
  Non-free: libfishcamp1t64, libsbig4t64 (camera libs, Debian non-free). Remove if the user wants a pure-free image.
- Windows apps are not shipped. Wine only runs what the user installs.

## Phone-home / telemetry
Checked: packages, enabled services and timers, listening and established sockets at idle.
- Established outbound connections at idle: none.
- Masked in the image: apt-daily, apt-daily-upgrade (+ services), fwupd-refresh (LVFS), avahi-daemon, ModemManager, cups-browsed.
- Removed/hidden: gnome-software autostart, update-notifier autostart, security-updates menu entry.
- KDE Connect: no autostart; runs only when the user opens Phone Link (LAN only, no cloud).
- Waydroid: downloads only if the user starts it.
- Listening at idle: CUPS on localhost 631 only.
- No telemetry/popcon/crash-reporter packages found.

## Hygiene and size
- Cleaned in image: apt lists and caches, docs, man pages, info, unused locales (English and Arabic kept), pyc, logs, machine-id.
- Failed units at idle: 0 (both editions). Idle RAM (selftest): see RESULTS below.
- Journal errors at boot are minor (portal pipewire client.conf, obexd evolution registry).

## RESULTS (filled from final-build evidence)
Final candidate: run 45908678140, head b18a82a, both editions, real boots in QEMU.
- Selftest: 58 PASS / 0 FAIL on Siraj and on Siraj Live.
- ISO size: Siraj 3,432,777,653 B; Siraj Live 3,432,930,620 B (about 3.43 GB each, no extra compression).
- Idle RAM at selftest: Siraj used 2656 MB / available 3275 MB; Live used 2680 MB / available 3251 MB (live overlay counted).
- Failed units: 0 on both.
- Stability (shorter than the 20-30 min goal, lab step time limit): 5 rounds of file manager + hilali + Wine notepad, free RAM flat, then no failed units, empty coredump directory, no segfault/OOM in dmesg or journal. Full edition proven; live edition: see report.
- Wine real apps: 7-Zip 26.06 and Notepad++ 8.9.9.1 installed and ran under Wine 10 on the full edition (lab 45895610838).
- Not proven: KDE Connect pairing and scrcpy with a real phone (no phone in the VM).
- Photo approval: the user approved the wallpapers in conversation (relayed by the main agent); this file is not itself evidence of that approval.
