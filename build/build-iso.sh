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
apt-get install -y -qq live-build debootstrap xorriso squashfs-tools syslinux-efi \
    isolinux syslinux-common librsvg2-bin python3 fonts-noto-core fonts-hosny-amiri \
    curl ca-certificates debian-archive-keyring > /dev/null
# Ubuntu's live-build package is too old for our config (no --bootloaders/--image-name).
# Overlay the current Debian live-build (arch-all, same deps just installed).
LB_DEB=$(curl -s https://deb.debian.org/debian/pool/main/l/live-build/ | grep -o 'live-build_[^"]*_all.deb' | sort -V | tail -1)
echo "==> Using Debian $LB_DEB"
curl -fsS -o /tmp/live-build.deb "https://deb.debian.org/debian/pool/main/l/live-build/$LB_DEB"
dpkg -i /tmp/live-build.deb > /dev/null || apt-get install -f -y -qq > /dev/null
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
echo "==> lb config ($VARIANT, $DEBIAN_SUITE/$ARCH)"
lb config \
  --distribution "$DEBIAN_SUITE" \
  --architectures "$ARCH" \
  --binary-images iso-hybrid \
  --debian-installer none \
  --bootappend-live "$BOOTAPPEND" \
  --archive-areas "main contrib non-free non-free-firmware" \
  --firmware-chroot true \
  --linux-flavours amd64 \
  --iso-volume "${ISO_PREFIX}-$(date +%Y%m%d)" \
  --iso-application "$OS_NAME 1.0 - Directed by Mohamed Sayed" \
  --image-name "$ISO_PREFIX" \
  --bootloaders "syslinux,grub-efi" \
  --memtest none \
  --zsync false

echo "==> Package lists"
mkdir -p config/package-lists
cp ../build/packages/*.list.chroot config/package-lists/
if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  cp ../build/packages/installer.list.chroot config/package-lists/
fi

echo "==> Includes (theme, skel, branding)"
cp -a ../build/includes.chroot config/
# Live variant: light-blue default theme (user request); full keeps aqua
if [ "$VARIANT" = "live" ]; then
  echo "==> Live variant: applying light-blue default theme"
  for f in config/includes.chroot/etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml \
           config/includes.chroot/etc/xdg/xfce4/panel/default.xml; do
    sed -i -e 's/value="0.03"/value="0.31"/' -e 's/value="0.35"/value="0.70"/' -e 's/value="0.33"/value="0.97"/' "$f"
  done
  sed -i -e 's/#08e8de/#4fb2f7/g' -e 's/rgba(47,191,169,.35)/rgba(79,178,247,.35)/g' \
    config/includes.chroot/etc/skel/.config/gtk-3.0/gtk.css
  find config/includes.chroot/usr/share/themes/CustomOS -name '*.xpm' -exec \
    sed -i 's/#08e8de/#4fb2f7/g; s/#52eee7/#83c9f9/g; s/#06aea6/#3b85b9/g' {} +
  sed -i 's/#08e8de #52eee7 #06aea6/#4fb2f7 #83c9f9 #3b85b9/' \
    config/includes.chroot/etc/skel/.config/customos/theme-colors
fi
# our fonts: runner needs them for artwork rendering, the ISO ships them
mkdir -p "$HOME/.local/share/fonts"
cp ../theme/fonts/*.ttf "$HOME/.local/share/fonts/" && fc-cache -f > /dev/null 2>&1 || true
mkdir -p config/includes.chroot/usr/share/fonts/truetype/customos
cp ../theme/fonts/*.ttf config/includes.chroot/usr/share/fonts/truetype/customos/
# OS name substitution across shipped files
grep -rl '@OS_NAME@' config/includes.chroot | while read -r f; do
  sed -i "s/@OS_NAME@/$OS_NAME/g" "$f"
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
# 3D perspective wallpaper (generated, not hand-drawn SVG)
python3 ../build/wallpaper3d/gen.py /tmp/horizon3d ../theme/crescent-moon.png
rsvg-convert -w 1920 -h 1080 /tmp/horizon3d/wallpaper-horizon3d.svg \
  -o config/includes.chroot/usr/share/backgrounds/customos/wallpaper-horizon3d.png

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
  sed -e "s/@OS_NAME@/$OS_NAME/g" -e 's/#eafefc/#eefaff/g' ../theme/boot/title.svg | rsvg-convert -o "$PLY/title.png"
else
  sed "s/@OS_NAME@/$OS_NAME/g" ../theme/boot/title.svg | rsvg-convert -o "$PLY/title.png"
fi

echo "==> Boot splash + ISO credits"
mkdir -p config/includes.binary/isolinux
if [ "$VARIANT" = "live" ]; then
  sed -e "s/@OS_NAME@/$OS_NAME/g" -e 's/#0a9d96/#2f8fdf/g' -e 's/#08e8de/#7fd4f7/g' -e 's/#eafefc/#eefaff/g' \
    ../theme/boot/splash.svg | rsvg-convert -w 640 -h 480 -o config/includes.binary/isolinux/splash.png
else
  sed "s/@OS_NAME@/$OS_NAME/g" ../theme/boot/splash.svg | rsvg-convert -w 640 -h 480 -o config/includes.binary/isolinux/splash.png
fi
printf '%s\n' "$OS_NAME (working title)" "Directed by Mohamed Sayed · محمد سيد" "Free and open-source software." "Moon imagery: NASA (public domain)." > config/includes.binary/CREDITS.txt

if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  echo "==> Calamares installer files (full variant)"
  mkdir -p config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares/branding config/includes.chroot/etc/skel/Desktop
  cp ../installer/calamares/settings.conf config/includes.chroot/etc/calamares/
  cp -a ../installer/calamares/branding/customos config/includes.chroot/usr/share/calamares/branding/
  cp ../installer/install-on-desktop.desktop config/includes.chroot/etc/skel/Desktop/
  sed -i "s/@OS_NAME@/$OS_NAME/g; s/@OS_NAME_AR@/$OS_NAME_AR/g" config/includes.chroot/etc/skel/Desktop/install-on-desktop.desktop
  grep -rl '@OS_NAME@' config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares | while read -r f; do sed -i "s/@OS_NAME@/$OS_NAME/g" "$f"; done || true
else
  echo "==> Live-only label"
  mkdir -p config/includes.chroot/etc/skel/Desktop
  printf '%s\n' "هذه النسخة التجريبية (Live): تعمل من الفلاشة فقط ولا تثبّت شيئاً على الجهاز." "This is the LIVE version: it runs from the USB stick only and installs nothing." "الحفظ الدائم (Persistence): عند حرق الفلاشة ببرنامج Rufus حرّك شريط Persistent partition size لحفظ ملفاتك وإعداداتك." "Persistence is supported: when burning with Rufus, set the Persistent partition size slider to keep your files and settings." > config/includes.chroot/etc/skel/Desktop/README-LIVE.txt
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
