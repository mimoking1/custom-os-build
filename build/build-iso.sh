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
    isolinux syslinux-common rsvg-convert python3 > /dev/null

echo "==> lb config ($VARIANT, $DEBIAN_SUITE/$ARCH)"
lb config \
  --distribution "$DEBIAN_SUITE" \
  --architectures "$ARCH" \
  --binary-images iso-hybrid \
  --debian-installer none \
  --bootappend-live "boot=live components quiet splash locales=en_US.UTF-8 keyboard-layouts=us,ara keyboard-options=grp:win_space_toggle" \
  --archive-areas "main contrib non-free non-free-firmware" \
  --firmware-chroot true \
  --linux-flavours amd64 \
  --iso-volume "${ISO_PREFIX}-$(date +%Y%m%d)" \
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
# OS name substitution across shipped files
grep -rl '@OS_NAME@' config/includes.chroot | while read -r f; do
  sed -i "s/@OS_NAME@/$OS_NAME/g" "$f"
done
grep -rl '@OS_NAME_AR@' config/includes.chroot | while read -r f; do
  sed -i "s/@OS_NAME_AR@/$OS_NAME_AR/g" "$f"
done

echo "==> Wallpaper render"
mkdir -p config/includes.chroot/usr/share/backgrounds/customos
rsvg-convert -w 1920 -h 1080 ../theme/wallpaper/wallpaper-dark.svg \
  -o config/includes.chroot/usr/share/backgrounds/customos/wallpaper-dark.png
rsvg-convert -w 1920 -h 1080 ../theme/wallpaper/wallpaper-light.svg \
  -o config/includes.chroot/usr/share/backgrounds/customos/wallpaper-light.png

if [ "$INCLUDE_INSTALLER" = "yes" ]; then
  echo "==> Calamares installer files (full variant)"
  mkdir -p config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares/branding config/includes.chroot/etc/skel/Desktop
  cp ../installer/calamares/settings.conf config/includes.chroot/etc/calamares/
  cp -a ../installer/calamares/branding/customos config/includes.chroot/usr/share/calamares/branding/
  cp ../installer/install-on-desktop.desktop config/includes.chroot/etc/skel/Desktop/
  grep -rl '@OS_NAME@' config/includes.chroot/etc/calamares config/includes.chroot/usr/share/calamares | while read -r f; do sed -i "s/@OS_NAME@/$OS_NAME/g" "$f"; done
else
  echo "==> Live-only label"
  mkdir -p config/includes.chroot/etc/skel/Desktop
  printf '%s\n' "هذه النسخة التجريبية (Live): تعمل من الفلاشة فقط ولا تثبّت شيئاً على الجهاز." "This is the LIVE version: it runs from the USB stick only and installs nothing." > config/includes.chroot/etc/skel/Desktop/README-LIVE.txt
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
ls -la
