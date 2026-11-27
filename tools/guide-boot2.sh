#!/usr/bin/env bash
# Boot an installed disk (no lab shell), screendump, log in by typing through the QEMU monitor.
# Usage: guide-boot2.sh disk.qcow2 outdir user pass
set -uo pipefail
DISK="$1"; OUT="$2"; U="$3"; P="$4"; mkdir -p "$OUT"; MON="$OUT/monitor.sock"
if [ -w /dev/kvm ]; then ACCEL="-enable-kvm"; else ACCEL="-accel tcg,thread=multi"; fi
qemu-system-x86_64 $ACCEL -m 4096 -smp 2 -drive file="$DISK",if=virtio -boot c -display none -vga virtio \
  -monitor unix:"$MON",server,nowait -netdev user,id=n0 -device virtio-net-pci,netdev=n0 &
Q=$!
m() { printf '%s\n' "$1" | socat - UNIX-CONNECT:"$MON" >/dev/null 2>&1; }
shot() { m "screendump $OUT/post-$1.ppm"; sleep 1; }
typ() { local s="$1" i c; for ((i=0;i<${#s};i++)); do c="${s:$i:1}"; case "$c" in [A-Z]) m "sendkey shift-$(echo $c | tr A-Z a-z)";; [a-z0-9]) m "sendkey $c";; '-') m "sendkey minus";; '_') m "sendkey shift-minus";; *) echo "skip char";; esac; sleep 0.3; done; }
sleep 20; shot 00-bootloader
sleep 70; shot 01-after-boot-70s
sleep 40; shot 02-after-boot-110s
typ "$U"; sleep 1; shot 03-username-typed; m "sendkey ret"; sleep 5; shot 04-password-prompt
typ "$P"; m "sendkey ret"; sleep 45; shot 05-desktop-45s
sleep 40; shot 06-desktop-85s
m "quit"; wait $Q 2>/dev/null
python3 - "$OUT" <<'PY'
import sys, os
from PIL import Image
for f in sorted(os.listdir(sys.argv[1])):
    if f.endswith('.ppm'):
        Image.open(os.path.join(sys.argv[1], f)).convert('RGB').save(os.path.join(sys.argv[1], f[:-4] + '.png')); print(f)
PY
