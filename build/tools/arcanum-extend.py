#!/usr/bin/env python3
"""Extend the Arcanum-Blue icon theme (GPL-3.0, StormRosenaa) so no icon the system uses falls
back to another theme. Names Arcanum already draws under a different name are copied (alias).
Names it has no art for are drawn here in the SAME construction as Arcanum's tiles:
dark rounded tile, blue base glow, grey gradient glyph with a soft drop shadow.
Usage: arcanum-extend.py <Arcanum-Blue dir>"""
import os, shutil, sys
root = sys.argv[1]
apps = os.path.join(root, "apps", "scalable")

ALIAS = {  # our name -> existing Arcanum icon
 "org.xfce.settings.manager":"org.gnome.Settings","org.xfce.panel":"org.gnome.Settings","org.xfce.settings.default-applications":"org.gnome.Settings",
 "org.xfce.settings.editor":"org.gnome.Settings","org.xfce.xfwm4-tweaks":"gnome-tweak-tool","org.xfce.terminal-settings":"org.gnome.Terminal.Preferences",
 "atril":"org.gnome.Evince","org.xfce.ristretto":"org.gnome.eog","org.xfce.mousepad":"accessories-text-editor","org.xfce.Dictionary":"accessories-text-editor",
 "simplescreenrecorder":"com.dec05eba.gpu_screen_recorder","calamares":"system-software-install","preferences-system-time":"org.gnome.clocks",
 "galculator":"org.gnome.Calculator","io.github.quodlibet.ExFalso":"org.strawberrymusicplayer.strawberry","io.github.quodlibet.QuodLibet":"org.strawberrymusicplayer.strawberry",
 "multimedia-volume-control":"org.pulseaudio.pavucontrol","org.xfce.parole":"org.videolan.VLC","org.xfce.thunar":"org.gnome.Nautilus","org.xfce.filemanager":"org.gnome.Nautilus",
 "system-file-manager":"org.gnome.Nautilus","xarchiver":"archivemanager","org.xfce.screenshooter":"com.system76.CosmicScreenshot","org.xfce.terminal":"org.gnome.Terminal",
 "org.xfce.terminalemulator":"org.gnome.Terminal","org.xfce.webbrowser":"brave-browser","web-browser":"brave-browser","org.xfce.settings.color":"gnome-color-manager",
 "org.xfce.mailreader":"thunderbird","org.xfce.settings.appearance":"gnome-tweak-tool","org.xfce.xfwm4":"org.gnome.Settings","org.xfce.settings.mouse":"org.gnome.Settings",
 "org.xfce.settings.keyboard":"org.gnome.Settings","org.xfce.settings.display":"org.gnome.Settings","org.xfce.settings.accessibility":"org.gnome.Settings",
 "org.xfce.session":"org.gnome.Settings","org.xfce.workspaces":"org.gnome.Settings","org.xfce.notification":"org.gnome.Settings","org.xfce.powermanager":"org.gnome.Settings",
 "org.xfce.volman":"org.gnome.Settings","org.xfce.xfdesktop":"org.gnome.eog","preferences-desktop-wallpaper":"org.gnome.eog","preferences-color":"gnome-color-manager",
 "org.xfce.taskmanager":"org.gnome.Logs","xfce-sensors":"org.gnome.Logs","org.xfce.about":"org.gnome.Settings","preferences-system-power-management":"org.gnome.Settings",
 "krita":"org.gnome.eog","org.xfce.appfinder":"org.gnome.Characters",
}
# glyph elements: P = paint (gradient or black), drawn in a 64x64 tile, content area ~14..50
def S(w,extra=""): return f'fill="none" stroke="P" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" {extra}'
GD = S(5, "stroke-dasharray='5.7 5.7'")
G = {
 "gear": f'<circle cx="32" cy="32" r="14.5" {GD}/><circle cx="32" cy="32" r="11" {S(4.5)}/><circle cx="32" cy="32" r="4" fill="P"/>',
 "info": f'<circle cx="32" cy="32" r="16" {S(4)}/><path d="M32 29v11" {S(4.5)}/><circle cx="32" cy="22.5" r="2.8" fill="P"/>',
 "clip": f'<rect x="17" y="16" width="30" height="34" rx="4" {S(4)}/><rect x="25" y="11" width="14" height="9" rx="3" fill="P"/><path d="M24 30h16M24 38h11" {S(3.5)}/>',
 "note": f'<path d="M19 13h20l8 8v30H19z" {S(4)}/><path d="M26 29h14M26 37h14M26 45h8" {S(3.5)}/>',
 "bell": f'<path d="M20 42V30a12 12 0 0124 0v12l4 4H16z" {S(4)}/><path d="M28 51a4 4 0 008 0" {S(3.5)}/>',
 "battery": f'<rect x="12" y="22" width="34" height="20" rx="4" {S(4)}/><rect x="48" y="28" width="4" height="8" rx="1.5" fill="P"/><rect x="17" y="27" width="17" height="10" rx="1.5" fill="P"/>',
 "smile": f'<circle cx="32" cy="32" r="17" {S(4)}/><circle cx="25.5" cy="27" r="2.5" fill="P"/><circle cx="38.5" cy="27" r="2.5" fill="P"/><path d="M24 36q8 8 16 0" {S(3.5)}/>',
 "clock": f'<circle cx="32" cy="32" r="17" {S(4)}/><path d="M32 21v11l8 5" {S(4)}/>',
 "image": f'<rect x="13" y="16" width="38" height="32" rx="4" {S(4)}/><circle cx="41" cy="25" r="3.5" fill="P"/><path d="M15 45l11-12 8 8 6-5 9 9z" fill="P"/>',
 "moon": '<path d="M37 13A19 19 0 1 0 51 38A15 15 0 1 1 37 13Z" fill="P"/><path d="M45 17l1.6 3.6 3.9.4-2.9 2.6.8 3.8-3.4-1.9-3.4 1.9.8-3.8-2.9-2.6 3.9-.4z" fill="P"/>',
 "brush": f'<path d="M45 14L28 33" {S(6)}/><path d="M26 33c-5 0-9 3-9 9 0 3-1 5-3 6 8 2 17 0 17-9z" fill="P"/>',
 "shield": f'<path d="M32 12l16 6v12c0 10-7 17-16 21-9-4-16-11-16-21V18z" {S(4)}/><path d="M25 32l5 5 9-10" {S(4)}/>',
 "palette": f'<path d="M32 13C21 13 13 21 13 32s8 19 17 19c4 0 5-3 3-6s0-6 4-6h6c4 0 8-3 8-7 0-9-8-19-19-19z" {S(4)}/><circle cx="24" cy="29" r="2.6" fill="P"/><circle cx="32" cy="23" r="2.6" fill="P"/><circle cx="40" cy="28" r="2.6" fill="P"/>',
 "usb": f'<rect x="14" y="26" width="30" height="14" rx="3" {S(4)}/><path d="M44 31h6M44 35h6" {S(3)}/><circle cx="21" cy="33" r="2" fill="P"/>',
 "disc": f'<circle cx="32" cy="32" r="18" {S(4)}/><circle cx="32" cy="32" r="5" {S(3.5)}/><path d="M42 20a15 15 0 013 5" {S(3)}/>',
 "monitor": f'<rect x="12" y="15" width="40" height="27" rx="4" {S(4)}/><path d="M26 50h12M32 42v8" {S(4)}/>',
 "keyboard": f'<rect x="11" y="20" width="42" height="24" rx="4" {S(4)}/><path d="M19 28h2M27 28h2M35 28h2M43 28h2M19 36h26" {S(3.5)}/>',
 "mouse": f'<rect x="21" y="12" width="22" height="40" rx="11" {S(4)}/><path d="M32 12v14M21 26h22" {S(3.5)}/>',
 "power": f'<path d="M23 20a16 16 0 1018 0" {S(4.5)}/><path d="M32 12v18" {S(4.5)}/>',
 "lock": f'<rect x="17" y="29" width="30" height="21" rx="4" {S(4)}/><path d="M23 29v-5a9 9 0 0118 0v5" {S(4)}/><circle cx="32" cy="39.500" r="3" fill="P"/>',
 "window": f'<rect x="12" y="15" width="40" height="34" rx="4" {S(4)}/><path d="M12 25h40" {S(4)}/>',
 "grid": '<rect x="14" y="14" width="15" height="15" rx="3" fill="P"/><rect x="35" y="14" width="15" height="15" rx="3" fill="P"/><rect x="14" y="35" width="15" height="15" rx="3" fill="P"/><rect x="35" y="35" width="15" height="15" rx="3" fill="P"/>',
 "person": f'<circle cx="32" cy="17" r="5" fill="P"/><path d="M16 26h32M32 26v11M32 37l-8 13M32 37l8 13" {S(4.5)}/>',
 "search": f'<circle cx="28" cy="28" r="12" {S(4.5)}/><path d="M37 37l12 12" {S(5.5)}/>',
 "book": f'<path d="M32 19c-5-4-12-5-18-4v31c6-1 13 0 18 4 5-4 12-5 18-4V15c-6-1-13 0-18 4zM32 19v31" {S(4)}/>',
 "mail": f'<rect x="12" y="17" width="40" height="30" rx="4" {S(4)}/><path d="M13 20l19 15 19-15" {S(4)}/>',
 "thermo": f'<path d="M28 14a4 4 0 018 0v20a9 9 0 11-8 0z" {S(4)}/><circle cx="32" cy="42" r="3.500" fill="P"/>',
 "graph": f'<path d="M14 14v36h36" {S(4)}/><path d="M20 40l9-10 7 6 11-14" {S(4)}/>',
 "scanner": f'<rect x="12" y="27" width="40" height="16" rx="4" {S(4)}/><path d="M18 35h28M18 20h28" {S(3.5)}/>',
 "play": '<path d="M22 15l26 17-26 17z" fill="P"/>',
 "speaker": f'<path d="M14 26h8l10-8v28l-10-8h-8z" fill="P"/><path d="M39 25a10 10 0 010 14M44 20a17 17 0 010 24" {S(3.5)}/>',
 "plus": f'<path d="M32 15v34M15 32h34" {S(6)}/>',
 "folder": '<path d="M12 22a4 4 0 014-4h10l5 6h17a4 4 0 014 4v18a4 4 0 01-4 4H16a4 4 0 01-4-4z" fill="P"/>',
 "doc": f'<path d="M19 13h20l8 8v30H19z" {S(4)}/><path d="M39 13v8h8" {S(3.5)}/>',
 "save": f'<path d="M15 15h28l6 6v28H15z" {S(4)}/><path d="M23 15v10h16V15M22 49V36h20v13" {S(3.5)}/>',
 "copy": f'<rect x="24" y="24" width="26" height="26" rx="4" {S(4)}/><path d="M40 24V17a3 3 0 00-3-3H17a3 3 0 00-3 3v20a3 3 0 003 3h7" {S(4)}/>',
 "trash": f'<path d="M16 21h32M26 21v-5h12v5M19 21l2 29h22l2-29" {S(4)}/><path d="M28 29v14M36 29v14" {S(3.5)}/>',
 "home": f'<path d="M12 31L32 14l20 17M18 28v22h28V28" {S(4.5)}/>',
 "x": f'<path d="M17 17l30 30M47 17L17 47" {S(6)}/>',
 "question": f'<circle cx="32" cy="32" r="17" {S(4)}/><path d="M26 27a6 6 0 1111 2c-2 2-5 3-5 7" {S(4)}/><circle cx="32" cy="43" r="2.600" fill="P"/>',
 "warn": f'<path d="M32 14L52 49H12z" {S(4)}/><path d="M32 26v11" {S(4.5)}/><circle cx="32" cy="43.500" r="2.600" fill="P"/>',
 "error": f'<circle cx="32" cy="32" r="17" {S(4)}/><path d="M25 25l14 14M39 25L25 39" {S(4.5)}/>',
 "globe": f'<circle cx="32" cy="32" r="18" {S(4)}/><path d="M14 32h36M32 14c-9 9-9 27 0 36M32 14c9 9 9 27 0 36" {S(3.5)}/>',
 "up": f'<path d="M32 50V16M18 29l14-14 14 14" {S(6)}/>',
 "back": f'<path d="M50 32H16M29 18L15 32l14 14" {S(6)}/>',
 "refresh": f'<path d="M48 26a17 17 0 10 1 10" {S(5)}/><path d="M49 14v13H36" {S(5)}/>',
 "folder-d": '<path d="M12 22a4 4 0 014-4h10l5 6h17a4 4 0 014 4v18a4 4 0 01-4 4H16a4 4 0 01-4-4z" fill="P"/>',
 "music": f'<path d="M26 44V18l22-5v26" {S(4)}/><circle cx="21" cy="45" r="5" fill="P"/><circle cx="43" cy="40" r="5" fill="P"/>',
 "video": f'<rect x="12" y="19" width="30" height="26" rx="4" {S(4)}/><path d="M42 29l10-6v18l-10-6z" fill="P"/>',
 "zip": f'<path d="M19 13h20l8 8v30H19z" {S(4)}/><path d="M30 13v6M34 19v6M30 25v6M34 31v6" {S(3)}/><rect x="29" y="38" width="6" height="8" rx="1.500" fill="P"/>',
 "wifi": f'<path d="M13 28a27 27 0 0138 0M19 35a18 18 0 0126 0M25 42a9 9 0 0114 0" {S(4)}/><circle cx="32" cy="48" r="2.800" fill="P"/>',
 "term": f'<path d="M15 20l12 10-12 10" {S(5)}/><path d="M31 44h18" {S(5)}/>',
 "pdf": f'<path d="M19 13h20l8 8v30H19z" {S(4)}/><path d="M25 40h14M25 33h14" {S(3.5)}/>',
 "list-add": f'<path d="M32 15v34M15 32h34" {S(6)}/>',
}
# our name -> (glyph, kind) kind: tile or bare (action icons draw a bare glyph, no tile)
TILE = {
 "picom":"window","xfce4-clipman-plugin":"clip","org.xfce.notes":"note","org.xfce.notification":"bell","org.xfce.powermanager":"battery",
 "help-about":"info","face-smile":"smile","clock-language":"globe","display-im7.q16":"image",
 "preferences-system-power-management":"battery","security-high":"shield","preferences-color":"palette","preferences-desktop-wallpaper":"image",
 "org.xfce.volman":"usb","timeshift":"clock","stock_xfburn":"disc","org.xfce.settings.display":"monitor","org.xfce.settings.keyboard":"keyboard",
 "org.xfce.settings.mouse":"mouse","xfsm-logout":"power","org.xfce.session":"power","org.xfce.xfwm4":"window","org.xfce.workspaces":"grid",
 "org.xfce.about":"info","org.xfce.settings.accessibility":"person","org.xfce.appfinder":"search","org.xfce.Dictionary":"book",
 "org.xfce.mailreader":"mail","xfce-sensors":"thermo","org.xfce.taskmanager":"graph","xsane":"scanner","krita":"brush",
 "org.xfce.settings.appearance":"palette","org.xfce.xfdesktop":"image","org.xfce.settings.color":"palette","org.xfce.panel":"gear",
 "org.xfce.settings.manager":"gear","org.xfce.settings.editor":"gear","org.xfce.settings.default-applications":"gear","org.xfce.xfwm4-tweaks":"gear",
 "multimedia-volume-control":"speaker","org.xfce.parole":"play","io.github.quodlibet.QuodLibet":"music","io.github.quodlibet.ExFalso":"music",
 "org.xfce.mousepad":"note","atril":"pdf","org.xfce.ristretto":"image","org.xfce.screenshooter":"window","simplescreenrecorder":"video",
 "calamares":"disc","galculator":"plus","org.xfce.thunar":"folder","org.xfce.filemanager":"folder","xarchiver":"zip","org.xfce.terminal":"term",
 "org.xfce.terminalemulator":"term","org.xfce.terminal-settings":"term","org.xfce.webbrowser":"globe","web-browser":"globe","preferences-system-time":"clock",
 "org.xfce.settings.default-applications":"gear","system-file-manager":"folder",
}
BARE = {
 "document-open":"folder","document-save":"save","document-new":"doc","edit-copy":"copy","edit-paste":"clip","edit-delete":"trash","user-home":"home",
 "go-home":"home","audio-volume-high":"speaker","dialog-warning":"warn","dialog-error":"error","dialog-question":"question","dialog-information":"info",
 "go-up":"up","go-previous":"back","list-add":"plus","window-close":"x","view-refresh":"refresh","system-shutdown":"power","system-lock-screen":"lock",
 "network-wireless":"wifi","battery":"battery",
}
HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">'
DEFS = ('<defs><linearGradient id="gl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cccccc"/><stop offset="1" stop-color="#999999"/></linearGradient>'
 '<linearGradient id="tb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#252733"/><stop offset="1" stop-color="#3b3a42"/></linearGradient>'
 '<linearGradient id="gw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#071112"/><stop offset=".3125" stop-color="#0d3a5a"/><stop offset=".5" stop-color="#66beff"/><stop offset=".6875" stop-color="#0d3a5a"/><stop offset="1" stop-color="#071112"/></linearGradient>'
 '<filter id="bl" x="-.1" y="-.1" width="1.2" height="1.2"><feGaussianBlur stdDeviation="2"/></filter></defs>')
def tile():
    # same geometry as Arcanum's tile (g877 transform 1.1, offset -3.18,-3.21)
    r = 'x="8.35" width="47.27" height="47.27" rx="9.88" ry="9.65"'
    return ('<g transform="matrix(1.1,0,0,1.1,-3.1846,-3.2065)">'
     f'<rect {r} y="8.37" fill="#000" filter="url(#bl)"/>'
     f'<rect {r} y="8.37" fill="url(#gw)" stroke="#000" stroke-opacity=".6" stroke-width=".45"/>'
     f'<rect {r} y="6.55" fill="url(#tb)" stroke="#000" stroke-opacity=".6" stroke-width=".45"/>'
     f'<rect {r} y="6.55" fill="#fff" opacity=".05"/></g>')
def glyph(key, tiled):
    g = G[key]
    sh = g.replace('"P"', '"#000"')
    fi = g.replace('"P"', '"url(#gl)"')
    sc = "" if tiled else ' transform="translate(-0 0)"'
    return (f'<g opacity=".4" transform="translate(0,1.8)">{sh}</g><g>{fi}</g>')
def write(name, key, tiled):
    body = (tile() if tiled else '') + glyph(key, tiled)
    if not tiled:
        body = f'<g transform="translate(32 32) scale(1.12) translate(-32 -32)">{glyph(key, False)}</g>'
    open(os.path.join(apps, name + ".svg"), "w").write(HEAD + DEFS + body + "</svg>\n")
KEEP = {"folder","term","pdf","zip","video","music","speaker","play","globe","plus","image","gear"}
KEEPN = {"org.xfce.mousepad","org.xfce.screenshooter","calamares","preferences-system-time","org.xfce.mailreader","org.xfce.settings.color","org.xfce.settings.appearance","preferences-color","org.xfce.xfwm4-tweaks"}
made = []
for name, key in TILE.items():
    p = os.path.join(apps, name + ".svg")
    if name in ALIAS and (key in KEEP or name in KEEPN) and os.path.exists(os.path.join(apps, ALIAS[name] + ".svg")):
        shutil.copyfile(os.path.join(apps, ALIAS[name] + ".svg"), p); made.append((name, "alias:" + ALIAS[name]))
    else:
        write(name, key, True); made.append((name, "drawn:" + key))
for name, src in ALIAS.items():
    p = os.path.join(apps, name + ".svg")
    if not os.path.exists(p) and os.path.exists(os.path.join(apps, src + ".svg")):
        shutil.copyfile(os.path.join(apps, src + ".svg"), p); made.append((name, "alias:" + src))
for name, key in BARE.items():
    if not os.path.exists(os.path.join(apps, name + ".svg")) or name in ("user-home","system-file-manager","web-browser"):
        write(name, key, False); made.append((name, "drawn-bare:" + key))
for n, how in made: print("ARCANUM-EXT", n, how)
print("ARCANUM-EXT TOTAL", len(made))
