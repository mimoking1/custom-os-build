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
    isolinux syslinux-common librsvg2-bin python3 fonts-noto-core fonts-hosny-amiri > /dev/null

BOOTAPPEND="boot=live components quiet splash locales=en_US.UTF-8 keyboard-layouts=us,ara keyboard-options=grp:win_space_toggle,grp:alt_shift_toggle"
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

echo "==> Boot splash + ISO credits"
mkdir -p config/includes.binary/isolinux
sed "s/@OS_NAME@/$OS_NAME/g" ../theme/boot/splash.svg | rsvg-convert -w 640 -h 480 -o config/includes.binary/isolinux/splash.png
printf '%s\n' "$OS_NAME (working title)" "Directed by Mohamed Sayed · محمد سيد" "Free and open-source software." > config/includes.binary/CREDITS.txt

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
ls -la
