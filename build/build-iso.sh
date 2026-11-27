#!/usr/bin/env bash
# Builds one ISO variant with Debian live-build.
# Usage: sudo ./build-iso.sh variants/full.conf
set -euo pipefail
VARIANT_FILE="${1:?pass variants/full.conf or variants/live.conf}"
source "$VARIANT_FILE"
WORK="$(pwd)/lb-$VARIANT"
rm -rf "$WORK"; mkdir -p "$WORK"; cd "$WORK"

echo "==> Installing live-build tooling"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq live-build debootstrap xorriso squashfs-tools syslinux-efi grub-common grub-pc-bin grub-efi-amd64-bin mtools \
    isolinux syslinux-common librsvg2-bin python3 fonts-noto-core fonts-hosny-amiri \
    curl ca-certificates debian-archive-keyring python3-pil > /dev/null
# Ubuntu's live-build package is too old for our config (no --bootloaders/--image-name).
# Overlay the current Debian live-build (arch-all, same deps just installed).
LB_DEB=$(curl -s https://deb.debian.org/debian/pool/main/l/live-build/ | grep -o 'live-build_[^"]*_all.deb' | sort -V | tail -1)
echo "==> Using Debian $LB_DEB"
curl -fsS -o /tmp/live-build.deb "https://deb.debian.org/debian/pool/main/l/live-build/$LB_DEB"
dpkg -i /tmp/live-build.deb > /dev/null || apt-get install -f -y -qq > /dev/null
# 4s auto-boot on the USB menu (default templates wait forever: timeout 0)
sed -i 's/^timeout .*/timeout 40/' \
  /usr/share/live/build/bootloaders/isolinux/isolinux.cfg \
  /usr/share/live/build/bootloaders/syslinux/syslinux.cfg 2>/dev/null || true
sed -i 's/^set timeout=.*/set timeout=4/' \
  /usr/share/live/build/bootloaders/grub-efi/grub.cfg 2>/dev/null || true
# Center the live entries' text on the glass buttons (GRUB themes cannot center item text):
# 643px buttons, Comfortaa Bold 29 (space 8.55px) -> 20/7 leading spaces
sed -i 's|Grub_live_menu_entry "Live system (${_FLAVOUR})"|Grub_live_menu_entry "                 Live system (${_FLAVOUR})"|' /usr/lib/live/build/binary_grub_cfg
sed -i 's|Grub_live_menu_entry "Live system (${_FLAVOUR} fail-safe mode)"|Grub_live_menu_entry "     Live system (${_FLAVOUR} fail-safe mode)"|' /usr/lib/live/build/binary_grub_cfg
# debootstrap must know the target suite
if [ ! -e "/usr/share/debootstrap/scripts/$DEBIAN_SUITE" ]; then
  DB_DEB=$(curl -s https://deb.debian.org/debian/pool/main/d/debootstrap/ | grep -o 'debootstrap_[^"]*_all.deb' | sort -V | tail -1)
  curl -fsS -o /tmp/debootstrap.deb "https://deb.debian.org/debian/pool/main/d/debootstrap/$DB_DEB"
  dpkg -i /tmp/debootstrap.deb > /dev/null
fi

BOOTAPPEND="boot=live components quiet splash console=ttyS0 locales=en_US.UTF-8 keyboard-layouts=us,ara keyboard-options=grp:win_space_toggle,grp:alt_shift_toggle"
if [ "$VARIANT" = "live" ]; then
  BOOTAPPEND="$BOOTAPPEND persistence persistence-label=persistence"
fi
if [ "$ARCH" = "i386" ]; then KFLAVOUR="686-pae"; BOOTLOADERS="syslinux"; else KFLAVOUR="amd64"; BOOTLOADERS="grub-pc,grub-efi"; fi
echo "==> lb config ($VARIANT, $DEBIAN_SUITE/$ARCH)"
lb config \
  --distribution "$DEBIAN_SUITE" \
  --architectures "$ARCH" \
  --binary-images iso-hybrid \
  --debian-installer none \
  --bootappend-live "$BOOTAPPEND" \
  --archive-areas "main contrib non-free non-free-firmware" \
  --firmware-chroot true \
  --linux-flavours "$KFLAVOUR" \
  --iso-volume "${ISO_PREFIX}-$(date +%Y%m%d)" \
  --iso-application "$OS_NAME 1.0 - Directed by Mohamed Sayed" \
  --image-name "$ISO_PREFIX" \
  --bootloaders "$BOOTLOADERS" \
  --memtest none \
  --zsync false \
  --chroot-squashfs-compression-type zstd

echo "==> Package lists"
mkdir -p config/package-lists
cp ../build/packages/*.list.chroot config/package-lists/
if [ "${LITE:-no}" = "yes" ]; then
  # 32-bit lite: no heavy creative apps, no flatpak store (Flathub has no i386)
  sed -i -E '/^(kdenlive|krita|inkscape|gimp|flatpak|gnome-software|gnome-software-plugin-flatpak|xdg-desktop-portal-gtk|libreoffice-impress|simplescreenrecorder|xfce4-notes-plugin)$/d' config/package-lists/base.list.chroot
fi
if [ "${LITE:-no}" = "yes" ]; then
  # no supported 32-bit Firefox; Chromium is installed by the hilal-browser hook
  sed -i -E '/^firefox-esr/d' config/package-lists/base.list.chroot
fi
if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  cp ../build/packages/installer.list.chroot config/package-lists/
fi

echo "==> Includes (theme, skel, branding)"
cp -a ../build/includes.chroot config/
# every launcher in /usr/local/bin must be executable (git modes have bitten us)
chmod 755 config/includes.chroot/usr/local/bin/* 2>/dev/null || true
# Arcanum icon theme (GPL-3.0, https://codeberg.org/StormRosenaa/Arcanum), pinned by sha256, fetched at build time
echo "==> Arcanum icon theme"
curl -fsSL --retry 4 --retry-delay 15 --retry-all-errors -o /tmp/arcanum-blue.tar.xz "https://codeberg.org/StormRosenaa/Arcanum/raw/branch/main/Arcanum%20-%20Blue.tar.xz" \
  || curl -fsSL --retry 3 -o /tmp/arcanum-blue.tar.xz "https://github.com/mimoking1/custom-os-build/releases/download/ci-evidence/arcanum-blue-mirror.tar.xz"
echo "7bebebe179eb34c6c59e486ed940bda55b6e08bef61462c2ab1a36fc0f68dcbf  /tmp/arcanum-blue.tar.xz" | sha256sum -c -
mkdir -p config/includes.chroot/usr/share/icons
tar -xf /tmp/arcanum-blue.tar.xz -C config/includes.chroot/usr/share/icons
mv "config/includes.chroot/usr/share/icons/Arcanum - Blue" config/includes.chroot/usr/share/icons/Arcanum-Blue
sed -i 's/^Name=.*/Name=Arcanum-Blue/; s/^Inherits=.*/Inherits=Papirus-Dark,Adwaita,hicolor/' config/includes.chroot/usr/share/icons/Arcanum-Blue/index.theme
# taskbar buttons of file-manager windows must not be a dark tile on the blue bar: let Papirus (colored) supply these app icons
rm -f config/includes.chroot/usr/share/icons/Arcanum-Blue/places/scalable/user-home.svg config/includes.chroot/usr/share/icons/Arcanum-Blue/apps/scalable/system-file-manager.svg config/includes.chroot/usr/share/icons/Arcanum-Blue/apps/scalable/org.xfce.thunar*.svg config/includes.chroot/usr/share/icons/Arcanum-Blue/apps/scalable/thunar*.svg
# no fallbacks: alias/draw every icon name the system uses that Arcanum lacks (same tile construction)
python3 ../build/tools/arcanum-extend.py config/includes.chroot/usr/share/icons/Arcanum-Blue | tee /tmp/arcanum-ext.log | tail -3
cp /tmp/arcanum-ext.log config/includes.chroot/usr/share/customos-arcanum-ext.log
rm -f /tmp/arcanum-blue.tar.xz
# Pexels photo wallpapers (private payload, not in the public repo; licence: Pexels, see LICENSING-AUDIT.md)
mkdir -p config/includes.chroot/usr/share/backgrounds/customos/gallery
for f in ../build/private/wall-*.jpg; do [ -e "$f" ] && cp "$f" "config/includes.chroot/usr/share/backgrounds/customos/gallery/$(basename "$f" | sed 's/^wall-//')"; done
# Tahmeel: native Linux build (Electron, no Wine) from the private payload, sha256-pinned
echo "==> Tahmeel: native Linux build"
PRIV=../build/private
[ -s "$PRIV/tahmeel-linux-x64.tar.xz" ] || { echo "Tahmeel native payload missing"; exit 1; }
echo "2a2206fd9efb02ca06a1dd89cf844db12b7c76ebafa6bceab17b1d76003ccbb0  $PRIV/tahmeel-linux-x64.tar.xz" | sha256sum -c -
echo "d4f02bb37a643b4a1dfbeff3371ea005340b94f29dd57c843f4432aee0e0ccb8  $PRIV/hilal-integration.tar.gz" | sha256sum -c -
TAH=config/includes.chroot/opt/tahmeel
mkdir -p "$TAH" /tmp/tah-int
tar -xJf "$PRIV/tahmeel-linux-x64.tar.xz" -C "$TAH" --strip-components=1
tar -xzf "$PRIV/hilal-integration.tar.gz" -C /tmp/tah-int
[ -x "$TAH/tahmeel-launch" ] || { echo "tahmeel-launch missing after extraction"; exit 1; }
mkdir -p "$TAH/extension" config/includes.chroot/etc/xdg/autostart config/includes.chroot/usr/share/applications
cp /tmp/tah-int/pkg/tahmeel.crx /tmp/tah-int/pkg/update.xml /tmp/tah-int/pkg/tahmeel.xpi "$TAH/extension/"
chmod 0644 "$TAH"/extension/*; chmod 0755 "$TAH/extension"
cp /tmp/tah-int/pkg/tahmeel-autostart.desktop config/includes.chroot/etc/xdg/autostart/
cp /tmp/tah-int/pkg/tahmeel.desktop config/includes.chroot/usr/share/applications/customos-tahmeel.desktop
chmod 755 "$TAH/tahmeel-launch"
# PRIVACY: hardened launcher. Chromium/Electron background networking, component updates, CDM downloads, safe-browsing, sync, pings and crash upload are all off; Google update/CDM hosts are also mapped to nothing.
cat > "$TAH/tahmeel-launch" <<'LEOF'
#!/bin/sh
# Tahmeel launcher. --no-sandbox because chrome-sandbox is not setuid in /opt; the app only loads its own local UI.
D="$(dirname "$(readlink -f "$0")")"
exec "$D/tahmeel" --no-sandbox --disable-gpu \
  --disable-component-update --disable-background-networking --disable-sync --disable-breakpad \
  --disable-domain-reliability --no-pings --no-default-browser-check --disable-client-side-phishing-detection \
  --disable-field-trial-config --disable-component-extensions-with-background-pages \
  --disable-features=OptimizationHints,MediaRouter,Translate,AutofillServerCommunication,NetworkTimeServiceQuerying,CertificateTransparencyComponentUpdater,WidevineCdm \
  --host-resolver-rules="MAP *.gvt1.com ~NOTFOUND, MAP *.gvt2.com ~NOTFOUND, MAP update.googleapis.com ~NOTFOUND, MAP clients2.google.com ~NOTFOUND, MAP clients1.google.com ~NOTFOUND, MAP safebrowsing.googleapis.com ~NOTFOUND, MAP optimizationguide-pa.googleapis.com ~NOTFOUND" \
  "$@"
LEOF
chmod 755 "$TAH/tahmeel-launch"
. ../build/browser-name.conf
mkdir -p config/includes.chroot/usr/share/customos
cp ../build/browser-name.conf config/includes.chroot/usr/share/customos/browser.conf
mkdir -p config/includes.chroot/usr/share/customos/home
sed -e "s/@BROWSER_NAME@/$BROWSER_NAME/g" -e "s/@BROWSER_NAME_AR@/$BROWSER_NAME_AR/g" ../build/browser-home.html > config/includes.chroot/usr/share/customos/home/browser-home.html
grep -rl "@BROWSER_NAME" config/includes.chroot | xargs sed -i -e "s/@BROWSER_NAME_AR@/$BROWSER_NAME_AR/g" -e "s/@BROWSER_NAME@/$BROWSER_NAME/g"
if [ "${LITE:-no}" = "yes" ]; then
  # 32-bit editions: smaller gallery (1920x1080) to keep the ISO light
  python3 - config/includes.chroot/usr/share/backgrounds/customos/gallery <<'PY'
import sys, glob
from PIL import Image
for f in glob.glob(sys.argv[1] + "/*.jpg") + glob.glob(sys.argv[1] + "/*.png"):
    im = Image.open(f)
    if im.width > 1920:
        im.convert("RGB").resize((1920, 1080), Image.LANCZOS).save(f, quality=92) if f.endswith(".jpg") else im.resize((1920, 1080), Image.LANCZOS).save(f)
PY
fi
# Live variant: light-blue default theme (user request); full keeps aqua
if [ "$VARIANT" = "live" ]; then
  echo "==> Live variant: applying light-blue default theme"
  sed -i -e 's/#08e8de/#4fb2f7/g' -e 's/rgba(47,191,169,.35)/rgba(79,178,247,.35)/g' \
    config/includes.chroot/etc/skel/.config/gtk-3.0/gtk.css
  find config/includes.chroot/usr/share/themes/Siraj -name '*.xpm' -exec \
    sed -i 's/#08e8de/#4fb2f7/g; s/#52eee7/#83c9f9/g; s/#06aea6/#3b85b9/g' {} +
  sed -i 's/#08e8de #52eee7 #06aea6/#4fb2f7 #83c9f9 #3b85b9/' \
    config/includes.chroot/etc/skel/.config/customos/theme-colors
fi
# no automatic updates in ANY edition: mask the apt timers/services with /dev/null links
mkdir -p config/includes.chroot/etc/systemd/system
# also mask phone-home / unneeded background items: LVFS firmware refresh, mDNS, modem, printer auto-discovery, kdeconnect autostart
for u in apt-daily.timer apt-daily-upgrade.timer apt-daily.service apt-daily-upgrade.service fwupd-refresh.timer fwupd-refresh.service avahi-daemon.service avahi-daemon.socket ModemManager.service cups-browsed.service; do
  ln -sf /dev/null "config/includes.chroot/etc/systemd/system/$u"
done
# our fonts: runner needs them for artwork rendering, the ISO ships them
mkdir -p "$HOME/.local/share/fonts"
cp ../theme/fonts/*.ttf "$HOME/.local/share/fonts/" && fc-cache -f > /dev/null 2>&1 || true
mkdir -p config/includes.chroot/usr/share/fonts/truetype/customos
cp ../theme/fonts/*.ttf config/includes.chroot/usr/share/fonts/truetype/customos/
# OS name substitution across shipped files
grep -rl -e '@OS_NAME@' -e '@OS_NAME_AR@' config/includes.chroot | while read -r f; do
  sed -i "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" "$f"
done || true
grep -rl '@OS_NAME_AR@' config/includes.chroot | while read -r f; do
  sed -i "s/@OS_NAME_AR@/$OS_NAME_AR/g" "$f"
done || true

echo "==> Wallpaper render"
mkdir -p config/includes.chroot/usr/share/backgrounds/customos
for WP in ../theme/wallpaper/*.svg; do
  rsvg-convert -w 1920 -h 1080 "$WP" \
    -o "config/includes.chroot/usr/share/backgrounds/customos/$(basename "$WP" .svg).png"
done
# Login-screen background (user choice): variant image + signature, replaces the gold-arch login image
python3 - "../theme/login/login-$VARIANT.png" "$VARIANT" /tmp/login-bg.svg <<'PYEOF'
import sys,base64
src,var,out=sys.argv[1:4]
b=base64.b64encode(open(src,'rb').read()).decode()
col='#0a5f5b' if var=='full' else '#1b4f86'
open(out,'w').write('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1920" height="1080" viewBox="0 0 1920 1080"><image width="1920" height="1080" xlink:href="data:image/png;base64,%s"/><text x="960" y="1050" text-anchor="middle" font-family="Noto Sans, Noto Sans Arabic, sans-serif" font-size="22" fill="%s">Directed by Mohamed Sayed &#183; &#1605;&#1581;&#1605;&#1583; &#1587;&#1610;&#1583;</text></svg>'%(b,col))
PYEOF
rsvg-convert -w 1920 -h 1080 /tmp/login-bg.svg -o config/includes.chroot/usr/share/backgrounds/customos/login-bg.png
sed -i 's#^background = .*#background = /usr/share/backgrounds/customos/login-bg.png#' config/includes.chroot/etc/lightdm/lightdm-gtk-greeter.conf
# 3D perspective wallpaper (generated, not hand-drawn SVG)
python3 ../build/wallpaper3d/gen.py /tmp/horizon3d ../theme/crescent-moon.png
rsvg-convert -w 1920 -h 1080 /tmp/horizon3d/wallpaper-horizon3d.svg \
  -o config/includes.chroot/usr/share/backgrounds/customos/wallpaper-horizon3d.png

echo "==> Default theme assets (icons, orb, glass panel, wallpaper) for $VARIANT"
CHR="$(pwd)/config/includes.chroot"
if [ "$VARIANT" = "live" ]; then ACC="#4fb2f7"; else ACC="#08e8de"; fi
# default accent of this edition (full = aqua #08e8de, live = sky #4fb2f7): panel-fix, hilali and the theme picker read it
mkdir -p config/includes.chroot/etc/skel/.config/customos
printf "%s\n" "$ACC" > config/includes.chroot/etc/skel/.config/customos/accent
export CUSTOMOS_SRC="$(pwd)/../build/includes.chroot/usr/share/customos/theme"
export CUSTOMOS_BASE_WALL="$CHR/usr/share/backgrounds/customos/wallpaper-horizon3d.png"
export CUSTOMOS_CRESCENT="$(pwd)/../theme/crescent-moon.png"
python3 ../build/includes.chroot/usr/local/bin/customos-theme-render --hex "$ACC" --target system --root "$CHR" --only all
CUSTOMOS_CRESCENT="$(pwd)/../theme/crescent-moon.png" python3 ../build/includes.chroot/usr/local/bin/customos-browser-icon --hex "$ACC" --root "$CHR"
FAV=$(find "$CHR/usr/share/icons/hicolor" -name hilal-browser.png | sort -V | tail -1); [ -n "$FAV" ] && python3 -c "import base64,sys;print(\"data:image/png;base64,\"+base64.b64encode(open(sys.argv[1],\"rb\").read()).decode())" "$FAV" > /tmp/favicon.txt && python3 - "$CHR/usr/share/customos/home/browser-home.html" <<'PY'
import sys;p=sys.argv[1];s=open(p).read().replace("@FAVICON@",open("/tmp/favicon.txt").read().strip());open(p,"w").write(s)
PY
cat "$CHR/etc/skel/.config/customos/panel.css" >> "$CHR/etc/skel/.config/gtk-3.0/gtk.css"
if [ "$VARIANT" = "live" ]; then
  python3 ../build/includes.chroot/usr/local/bin/customos-theme-render --default-live-wallpaper "$CHR/usr/share/backgrounds/customos/wallpaper-default.png"
else
  cp "$CHR/usr/share/backgrounds/customos/wallpaper-horizon3d.png" "$CHR/usr/share/backgrounds/customos/wallpaper-default.png"
fi
DT="$CHR/etc/skel/Desktop"
if [ "$VARIANT" = "live" ]; then rm -f "$DT/70-guide.desktop"; else rm -f "$DT/69-live-guide.desktop" "$DT/71-guide-ar.desktop"; fi
unset CUSTOMOS_SRC CUSTOMOS_BASE_WALL CUSTOMOS_CRESCENT

echo "==> Plymouth boot animation (3D crescent flip)"
PLY=config/includes.chroot/usr/share/plymouth/themes/customos
mkdir -p "$PLY/frames"
cp ../build/plymouth/customos/customos.plymouth ../build/plymouth/customos/customos.script "$PLY/"
if [ "$VARIANT" = "live" ]; then
  sed -i -e 's/Window.SetBackgroundTopColor(0.03, 0.55, 0.52);/Window.SetBackgroundTopColor(0.184, 0.561, 0.875);/' \
         -e 's/Window.SetBackgroundBottomColor(0.03, 0.78, 0.74);/Window.SetBackgroundBottomColor(0.498, 0.831, 0.969);/' \
         "$PLY/customos.script"
fi
python3 ../build/plymouth/gen-frames.py ../theme/crescent-moon.png "$PLY/frames"
if [ "$VARIANT" = "live" ]; then
  sed -e "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" -e 's/#eafefc/#eefaff/g' ../theme/boot/title.svg | rsvg-convert -o "$PLY/title.png"
else
  sed "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" ../theme/boot/title.svg | rsvg-convert -o "$PLY/title.png"
fi

echo "==> Boot splash + ISO credits"
mkdir -p config/includes.binary/isolinux
if [ "$VARIANT" = "live" ]; then
  sed -e "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" -e 's/#0a9d96/#2f8fdf/g' -e 's/#08e8de/#7fd4f7/g' -e 's/#eafefc/#eefaff/g' \
    ../theme/boot/splash.svg | rsvg-convert -w 640 -h 480 -o config/includes.binary/isolinux/splash.png
else
  sed "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" ../theme/boot/splash.svg | rsvg-convert -w 640 -h 480 -o config/includes.binary/isolinux/splash.png
fi
printf '%s\n' "$OS_NAME_AR - $OS_NAME" "Directed by Mohamed Sayed · محمد سيد" "Free and open-source software." "Moon imagery: NASA (public domain)." > config/includes.binary/CREDITS.txt

echo "==> GRUB graphical boot theme (approved mockup look)"
# fonts must be visible to rsvg-convert for the title text
mkdir -p /usr/share/fonts/truetype/customos
cp ../theme/fonts/Comfortaa-Regular.ttf ../theme/fonts/Comfortaa-Bold.ttf ../theme/fonts/NotoKufiArabic-Bold.ttf /usr/share/fonts/truetype/customos/ 2>/dev/null || true
fc-cache -f > /dev/null 2>&1 || true
mkdir -p config/bootloaders/grub-pc/fonts
cp -a ../build/bootloaders/grub-pc/config.cfg ../build/bootloaders/grub-pc/theme.cfg ../build/bootloaders/grub-pc/grub.cfg config/bootloaders/grub-pc/
mkdir -p config/bootloaders/grub-pc/live-theme
cp -a ../build/bootloaders/grub-pc/live-theme/. config/bootloaders/grub-pc/live-theme/
# Boot menu background: recorded assignment FULL/installed = teal, LIVE = sky-blue
if [ "$VARIANT" = "live" ]; then BG_TOP="#1b6fc4"; BG_BOT="#63cdf5"; else BG_TOP="#0a9d96"; BG_BOT="#08e8de"; fi
sed -e "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" -e "s/@BG_TOP@/$BG_TOP/g; s/@BG_BOT@/$BG_BOT/g" ../theme/boot/grub-bg.svg | rsvg-convert -w 1024 -h 768 -o config/bootloaders/grub-pc/live-theme/background.png
grub-mkfont -s 29 -n "Comfortaa Bold" -o config/bootloaders/grub-pc/fonts/comfortaa-bold-29.pf2 ../theme/fonts/Comfortaa-Bold.ttf
grub-mkfont -s 13 -n "Comfortaa Regular" -o config/bootloaders/grub-pc/fonts/comfortaa-regular-13.pf2 ../theme/fonts/Comfortaa-Regular.ttf

if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  echo "==> Calamares installer files (full variant)"
  mkdir -p config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares/branding config/includes.chroot/etc/skel/Desktop
  cp ../installer/calamares/settings.conf config/includes.chroot/etc/calamares/
  mkdir -p config/includes.chroot/etc/calamares/modules && cp ../installer/calamares/modules/*.conf config/includes.chroot/etc/calamares/modules/
  cp -a ../installer/calamares/branding/customos config/includes.chroot/usr/share/calamares/branding/
  cp ../installer/install-on-desktop.desktop config/includes.chroot/etc/skel/Desktop/60-install.desktop
  sed -i "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" config/includes.chroot/etc/skel/Desktop/60-install.desktop
  grep -rl -e '@OS_NAME@' -e '@OS_NAME_AR@' config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares | while read -r f; do sed -i "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" "$f"; done || true
else
  echo "==> Live-only label"
  mkdir -p config/includes.chroot/etc/skel/Desktop config/includes.chroot/usr/share/customos/guides
  printf '%s\n' "هذه النسخة التجريبية (Live): تعمل من الفلاشة فقط ولا تثبّت شيئاً على الجهاز." "This is the LIVE version: it runs from the USB stick only and installs nothing." "الحفظ الدائم (Persistence): عند حرق الفلاشة ببرنامج Rufus حرّك شريط Persistent partition size لحفظ ملفاتك وإعداداتك." "Persistence is supported: when burning with Rufus, set the Persistent partition size slider to keep your files and settings." > config/includes.chroot/usr/share/customos/guides/README-LIVE.txt
fi

echo "==> Hooks"
cp ../build/hooks/*.hook.chroot config/hooks/normal/ 2>/dev/null || {
  mkdir -p config/hooks/normal && cp ../build/hooks/*.hook.chroot config/hooks/normal/; }
if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  cp ../build/hooks/installer-only/*.hook.chroot config/hooks/normal/
fi

echo "==> lb build (this is the long step)"
lb build

echo "==> Outputs"
mkdir -p ../out
mv "$ISO_PREFIX"*.iso ../out/ 2>/dev/null || mv live-image-*.iso "../out/$ISO_PREFIX-amd64.iso"
cd ../out
sha256sum *.iso | tee SHA256SUMS.txt
chmod -R a+rwX .  # let the runner user write boot-test output next to the ISOs
ls -la
