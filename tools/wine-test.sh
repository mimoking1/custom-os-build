#!/usr/bin/env bash
# Wine (proxy) + native test of Tahmeel v5. Shots and logs go to /tmp/wt-out.
O=/tmp/wt-out; mkdir -p $O
export DISPLAY=:99 WINEPREFIX=/tmp/wp WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
Xvfb :99 -screen 0 1280x800x24 >/dev/null 2>&1 &
sleep 3
shot(){ import -window root "$O/$1.png" 2>>$O/errors.log; }
now(){ date +%s.%N; }
wins(){ xdotool search --onlyvisible --name '.' 2>/dev/null | wc -l; }
log(){ echo "$@" | tee -a $O/summary.txt; }
S=$(ls /tmp/pl/*[sS]etup*.exe 2>/dev/null | head -1); P=$(ls /tmp/pl/*ortable*.exe 2>/dev/null | head -1)
log "setup=$S portable=$P"; sha256sum /tmp/pl/* | tee -a $O/summary.txt
wineboot -i >$O/wineboot.log 2>&1; sleep 5; wine --version | tee -a $O/summary.txt
shot 00-desktop

# ---- Setup ----
t0=$(now); wine "$S" >$O/setup-run.log 2>&1 &
first=""
for i in $(seq 1 120); do
  sleep 0.5
  if [ "$(wins)" -gt 0 ] && [ -z "$first" ]; then first=$(echo "$(now) - $t0" | bc); fi
  [ -n "$first" ] && break
done
log "SETUP first window after ${first:-none}s"
for k in 1 2 3 4 5 6 7 8; do
  sleep 6; shot "S$k-wizard"; xdotool key Return 2>/dev/null
done
sleep 40; shot S9-after
find $WINEPREFIX/drive_c -iname "*.exe" -ipath "*tahmeel*" 2>/dev/null | head | tee -a $O/summary.txt
INST=$(find $WINEPREFIX/drive_c -iname "tahmeel*.exe" -not -iname "*uninst*" 2>/dev/null | head -1)
log "installed exe: $INST"
if [ -n "$INST" ]; then
  t0=$(now); wine "$INST" >$O/setup-app.log 2>&1 &
  first=""; for i in $(seq 1 240); do sleep 0.5; w=$(xdotool search --onlyvisible --name 'ahmeel|تحميل' 2>/dev/null | wc -l); [ "$w" -gt 0 ] && { first=$(echo "$(now) - $t0" | bc); break; }; done
  log "SETUP-APP first Tahmeel window after ${first:-none}s"
  sleep 6; shot S10-main-window
  xdotool key ctrl+comma 2>/dev/null; sleep 3; shot S11-settings-try
  xdotool search --onlyvisible --name '.' getwindowname %@ 2>/dev/null | head -20 | tee -a $O/summary.txt
fi
wineserver -k; sleep 3
grep -ihE "asar|integrity|fatal|crash|error" $O/setup-*.log | head -20 | tee -a $O/summary.txt

# ---- Portable ----
ls $WINEPREFIX/drive_c/users/*/Temp 2>/dev/null | tee $O/temp-before.txt
t0=$(now); wine "$P" >$O/portable-run.log 2>&1 &
first=""; for i in $(seq 1 240); do sleep 0.5; w=$(xdotool search --onlyvisible --name 'ahmeel|تحميل' 2>/dev/null | wc -l); [ "$w" -gt 0 ] && { first=$(echo "$(now) - $t0" | bc); break; }; done
log "PORTABLE first Tahmeel window after ${first:-none}s"
sleep 8; shot P1-portable
ls -d $WINEPREFIX/drive_c/users/*/Temp/nst* 2>/dev/null | tee $O/nst-while-running.txt
log "nst while running: $(wc -l < $O/nst-while-running.txt)"
xdotool search --onlyvisible --name '.' getwindowname %@ 2>/dev/null | head -10 | tee -a $O/summary.txt
xdotool key alt+F4 2>/dev/null; sleep 6; shot P2-after-close
wineserver -k; sleep 4
ls -d $WINEPREFIX/drive_c/users/*/Temp/nst* 2>/dev/null | tee $O/nst-after.txt
log "nst after kill (NOT a tray Exit): $(wc -l < $O/nst-after.txt)"
grep -ihE "asar|integrity|fatal|crash" $O/portable-run.log | head | tee -a $O/summary.txt

# ---- Native Linux ----
L=$(ls /tmp/pl/tahmeel-linux-x64.tar.xz 2>/dev/null); mkdir -p /tmp/nat && tar -xJf "$L" -C /tmp/nat --strip-components=1
sha256sum "$L" | tee -a $O/summary.txt
t0=$(now); (cd /tmp/nat && ./tahmeel-launch --no-sandbox >$O/native-run.log 2>&1 &)
first=""; for i in $(seq 1 120); do sleep 0.5; w=$(xdotool search --onlyvisible --name 'ahmeel|تحميل' 2>/dev/null | wc -l); [ "$w" -gt 0 ] && { first=$(echo "$(now) - $t0" | bc); break; }; done
log "NATIVE first Tahmeel window after ${first:-none}s"
sleep 6; shot N1-native
tail -20 $O/native-run.log | tee -a $O/summary.txt
