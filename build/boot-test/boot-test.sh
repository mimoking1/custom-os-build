#!/usr/bin/env bash
# Boots an ISO in QEMU/KVM headless and captures staged screenshots + a boot log.
# Usage: ./boot-test.sh path/to.iso outdir
set -uo pipefail
ISO="${1:?iso path}"; OUT="${2:?out dir}"; mkdir -p "$OUT"
MON="$OUT/monitor.sock"
if [ -w /dev/kvm ]; then
  ACCEL="-enable-kvm"; TIMES="15 60 150 260"
else
  echo "KVM unavailable, falling back to TCG (slower)"
  ACCEL="-accel tcg,thread=multi"; TIMES="20 90 240 420"
fi
qemu-system-x86_64 \
  $ACCEL -m 3072 -smp 2 \
  -cdrom "$ISO" -boot d \
  -display none -vga virtio \
  -monitor unix:"$MON",server,nowait \
  -serial file:"$OUT/serial.log" \
  -netdev user,id=n0 -device virtio-net-pci,netdev=n0 &
QPID=$!
# capture the branded boot menu first, then auto-select the default entry
sleep 4
echo "screendump $EVIDENCE/shot-04s-menu.ppm" | socat - UNIX-CONNECT:"$MON" 2>/dev/null || printf 'screendump %s\n' "$EVIDENCE/shot-04s-menu.ppm" | nc -U "$MON"
convert "$EVIDENCE/shot-04s-menu.ppm" "$EVIDENCE/shot-04s-menu.png" 2>/dev/null || true
sleep 4
echo "sendkey ret" | socat - UNIX-CONNECT:"$MON" 2>/dev/null || printf 'sendkey ret
' | nc -U "$MON" || true
for t in $TIMES; do
  sleep "$([ "$t" = 15 ] && echo 15 || echo $((t - prev)))"; prev=$t
  echo "screendump $OUT/shot-${t}s.ppm" | socat - UNIX-CONNECT:"$MON" 2>/dev/null || \
    printf 'screendump %s\n' "$OUT/shot-${t}s.ppm" | nc -U "$MON" || true
done
sleep 5
kill $QPID 2>/dev/null; wait $QPID 2>/dev/null
python3 - "$OUT" <<'PY'
import sys, os
from PIL import Image
out = sys.argv[1]
ok = False
for f in sorted(os.listdir(out)):
    if f.endswith('.ppm'):
        im = Image.open(os.path.join(out, f)).convert('RGB')
        px = list(im.resize((64, 36)).getdata())
        # a working desktop is neither all-black nor a single color
        uniq = len(set(px))
        bright = sum(1 for p in px if sum(p) > 60)
        print(f"{f}: unique_colors={uniq} lit_pixels={bright}")
        if uniq > 40 and bright > 200:
            ok = True
        im.save(os.path.join(out, f.replace('.ppm', '.png')))
print("BOOT_TEST_RESULT:", "PASS (reached a rendered graphical screen)" if ok else "FAIL (screen never rendered)")
sys.exit(0 if ok else 1)
PY
