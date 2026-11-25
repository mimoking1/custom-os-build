#!/usr/bin/env bash
# Bar lab: boot an ISO, wait for the in-guest lab shell, then apply patch blocks
# from a plan file over the serial console, screendumping after each.
# Usage: ./bar-lab.sh path/to.iso outdir planfile
# Plan format: blocks separated by marker lines:
#   ===CMD===          guest shell block follows (runs in the desktop session)
#   ===SHOT name===    screendump to outdir/lab-<name>.ppm
set -uo pipefail
ISO="${1:?iso path}"; OUT="${2:?out dir}"; PLAN="${3:?plan file}"; mkdir -p "$OUT"
MON="$OUT/monitor.sock"; SER="$OUT/serial.sock"
mkdir -p "$OUT/hostshare"
if [ -w /dev/kvm ]; then ACCEL="-enable-kvm"; else ACCEL="-accel tcg,thread=multi"; fi
${QEMU_BIN:-qemu-system-x86_64} ${QEMU_CPU:+-cpu $QEMU_CPU} \
  $ACCEL -m 6144 -smp 2 \
  -cdrom "$ISO" -boot d \
  -display none -vga virtio \
  -monitor unix:"$MON",server,nowait \
  -serial unix:"$SER",server,nowait \
  -fw_cfg name=opt/customos/selftest,string=1 \
  -fw_cfg name=opt/customos/lab,string=1 \
  -virtfs local,path="$OUT/hostshare",mount_tag=hostshare,security_model=none \
  -netdev user,id=n0 -device virtio-net-pci,netdev=n0 &
QPID=$!

# boot menu proof + boot the default entry (same rhythm as boot-test)
sleep 3
printf 'screendump %s\n' "$OUT/lab-00-menu.ppm" | socat - UNIX-CONNECT:"$MON" >/dev/null 2>&1 || true
sleep 4
printf 'sendkey ret\n' | socat - UNIX-CONNECT:"$MON" >/dev/null 2>&1 || true

mkfifo "$OUT/ser.in"
socat UNIX-CONNECT:"$SER",retry=30,interval=1 - < "$OUT/ser.in" > "$OUT/ser.log" 2>/dev/null &
SOC=$!
exec 9>"$OUT/ser.in"   # hold the fifo writer open for the run

wait_marker() {  # wait for Nth occurrence of $1 in ser.log, timeout $2 (s)
  local pat="$1" n="$2" tmo="${3:-240}" t0=$SECONDS
  while [ $((SECONDS - t0)) -lt "$tmo" ]; do
    [ "$(grep -ac "$pat" "$OUT/ser.log" 2>/dev/null || echo 0)" -ge "$n" ] && return 0
    sleep 2
  done
  return 1
}

echo "waiting for LAB-READY..."
if ! wait_marker "LAB-READY" 1 900; then
  echo "LAB-READY never arrived; tail of serial:"; tail -30 "$OUT/ser.log"
  kill $QPID $SOC 2>/dev/null; exec 9>&-; exit 1
fi
wait_marker "LAB-SHELL-UP" 1 60 || echo "warn: no LAB-SHELL-UP"

send_block() {  # $1 = shell file to upload+run in the guest
  printf 'BEGIN\n' >&9
  base64 -w0 "$1" | fold -w 900 | while read -r c; do printf 'W %s\n' "$c" >&9; done
  printf 'RUN\n' >&9
}

DONES=0
run_cmd_block() {  # $1 = shell file
  send_block "$1"
  DONES=$((DONES+1))
  wait_marker "LAB-CMD-DONE" "$DONES" 300 || echo "warn: LAB-CMD-DONE $DONES missed"
  sleep 1
}
shot() {  # $1 = name
  sleep 3
  printf 'screendump %s\n' "$OUT/lab-$1.ppm" | socat - UNIX-CONNECT:"$MON" >/dev/null 2>&1 || true
  sleep 2
}

# walk the plan
cur=""
flush() { [ -n "$cur" ] && { run_cmd_block "$cur"; : > "$cur"; }; }
while IFS= read -r line; do
  case "$line" in
    ===CMD===)     flush ;;
    ===SHOT*===)   flush; n=$(echo "$line" | sed 's/===SHOT *//; s/===//; s/[^A-Za-z0-9._-]/_/g'); shot "$n" ;;
    *) [ -z "$cur" ] && cur=$(mktemp); printf '%s\n' "$line" >> "$cur" ;;
  esac
done < "$PLAN"
flush

exec 9>&-
tail -80 "$OUT/ser.log" | grep -a "LAB-" | tail -20 || true
kill $QPID $SOC 2>/dev/null; wait 2>/dev/null
python3 - "$OUT" <<'PY'
import sys, os
from PIL import Image
out = sys.argv[1]
for f in sorted(os.listdir(out)):
    if f.endswith('.ppm'):
        Image.open(os.path.join(out, f)).convert('RGB').save(os.path.join(out, f.replace('.ppm', '.png')))
        print('shot:', f.replace('.ppm', '.png'))
PY
