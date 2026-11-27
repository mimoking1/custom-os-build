#!/usr/bin/env bash
# Make a TEST copy of the release ISO: adds the CI selftest as an extra squashfs layer in /live.
# The release ISO itself carries no test code. Usage: make-test-iso.sh release.iso test.iso
set -euo pipefail
REL="$1"; OUT="$2"
sudo apt-get install -y -qq squashfs-tools xorriso >/dev/null
sudo mksquashfs build/testoverlay /tmp/zz-test.squashfs -all-root -noappend -comp gzip >/dev/null
rm -f "$OUT"
xorriso -indev "$REL" -outdev "$OUT" -boot_image any replay -map /tmp/zz-test.squashfs /live/zz-test.squashfs -commit 2>&1 | tail -3
ls -la "$REL" "$OUT"
