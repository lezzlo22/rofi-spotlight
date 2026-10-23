# rofi-spotlight

Spotlight-style launcher built on plain [rofi](https://github.com/davatorium/rofi) (rofi 1.7.5+). No extra packages, no WM lock-in.

One box: open windows, apps, then everyday files as you type. Text that matches nothing + Enter → web search (or opens it directly if it looks like a URL).

| Key | Does |
|---|---|
| type | filter windows, apps, files (~9k entries, up to 5 folders deep under `~`) |
| Enter | open the highlighted result |
| Ctrl+Enter | web search the typed text even if something matches |
| Ctrl+Tab → Enter → type | deep search: every file under `~` (~127k, takes ~2s to load) |
| `!f` / `!d` / `!wi` prefix | only files / apps / windows |

## Install

```bash
# 1. put it where rofi looks (or clone elsewhere and symlink ~/.config/rofi -> the clone)
git clone https://github.com/lezzlo22/rofi-spotlight ~/.config/rofi
cd ~/.config/rofi
ln -sf files.sh scripts/files-quick.sh      # script self-detects its two roles via $0

# 2. colors
#   a) with pywal — live, follows your wallpaper:
cp templates/colors-rofi-spotlight.rasi ~/.config/wal/templates/
wal -R                                       # regenerate now (also runs at login via your wal hook)
ln -sf ~/.cache/wal/colors-rofi-spotlight.rasi colors-wal.rasi
#   b) without pywal — static:
# cp colors-wal.rasi.example colors-wal.rasi

# 3. bind a key to the launcher. Examples:
#   i3:    bindsym $mod+d exec --no-startup-id ~/.config/rofi/launch
#   sway:  bindsym $mod+d exec ~/.config/rofi/launch
#   XFCE:  xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Primary><Alt>r' -n -t string -s "$HOME/.config/rofi/launch"
```

Nothing is hardcoded to a user or home path: `launch` resolves the script paths from its own location at runtime (rofi doesn't expand `~`/`$HOME` in mode paths, so they can't live in `config.rasi`).

**Dependencies:** `rofi`, `python3`, `xdg-utils` (`xdg-open`), `util-linux` (`setsid`), and an icon theme — `Papirus-Dark` by default; change `icon-theme` in `config.rasi` to one you have.

## Files

- `launch`: portable entry point — derives absolute script paths from its own dir and runs `rofi -show combi`. Bind your hotkey to this.
- `config.rasi`: modes-free options + Spotlight-style theme (centered box). Imports `colors-wal.rasi` for the palette.
- `colors-wal.rasi`: the live palette (`@bg`/`@fg`/`@accent`/`@sel-fg`). Normally a symlink to the pywal output; or a copy of `colors-wal.rasi.example`. Git-ignored (per-machine).
- `templates/colors-rofi-spotlight.rasi`: pywal template → `~/.cache/wal/colors-rofi-spotlight.rasi`. Change the color indices (`color1`..`color6`) for a different accent.
- `colors-wal.rasi.example`: static fallback palette (Catppuccin Mocha + Mauve) for non-pywal setups.
- `scripts/files.sh`: file list mode. As `files-quick.sh` (symlink) it lists everyday files for the main box; as `files.sh` it's the lazy deep-search tab.
- `scripts/web.sh`: receives unmatched text → opens URL or Google search in the default browser.

## Notes / gotchas

- Fonts use the generic `sans-serif` alias → whatever your system's default sans is. Change `font` in `config.rasi` for a specific face.
- The frosted `bg` alpha only shows with a running compositor (picom, etc.); without one it renders opaque.
- rofi loads **every** mode at startup, so the deep tab only shows a "Load all files" entry until Enter — otherwise the main box takes ~0.7s to open.
- Keep `listview { fixed-height: true; }`; with `false` rofi measures every row (1.7s with many files).
- Don't enable `drun-use-desktop-cache`: it keeps showing uninstalled apps and only saves ~8ms.
- Rofi's theme parser misreads a quoted string followed by another quoted value in the same block, so `entry` properties are split over several blocks.
- Opening uses `xdg-open`; a file type with no default app opens nothing (`xdg-mime default <app>.desktop <mime>`).
- The `src`/`lib`/`jdk*`/`netbeans*` prune names in `files.sh` just trim noise; harmless if you don't have them.
