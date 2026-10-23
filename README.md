# rofi-spotlight

Spotlight-style launcher built on plain [rofi](https://github.com/davatorium/rofi) (rofi 1.7.5+). No extra packages, no WM lock-in, **themed out of the box** (Catppuccin Mocha), and **fully self-contained** — it never reads or overwrites your `~/.config/rofi/config.rasi`, so other rofi-based tools (volume menus, calendars, etc.) keep working untouched.

One box: open windows, apps, then everyday files as you type. Text that matches nothing + Enter → web search (or opens it directly if it looks like a URL).

| Key | Does |
|---|---|
| type | filter windows, apps, files (~9k entries, up to 5 folders deep under `~`) |
| Enter | open the highlighted result |
| Ctrl+Enter | web search the typed text even if something matches |
| Ctrl+Tab → Enter → type | deep search: every file under `~` (~127k, takes ~2s to load) |
| `!f` / `!d` / `!wi` prefix | only files / apps / windows |

## Install

Clone to its **own** directory (not `~/.config/rofi`, so nothing collides):

```bash
# 1. clone anywhere standalone
git clone https://github.com/lezzlo22/rofi-spotlight ~/.config/rofi-spotlight
cd ~/.config/rofi-spotlight
ln -sf files.sh scripts/files-quick.sh      # script self-detects its two roles via $0

# 2. (optional) override the built-in Catppuccin theme. Skip this to keep it.
#   a) pywal — live, follows your wallpaper:
cp templates/colors-rofi-spotlight.rasi ~/.config/wal/templates/
wal -R                                       # regenerate now (also runs at login via your wal hook)
ln -sf ~/.cache/wal/colors-rofi-spotlight.rasi colors-wal.rasi
#   b) custom static palette:
# cp colors-wal.rasi.example colors-wal.rasi  # then edit the 4 colors

# 3. bind a key to the launcher. Examples:
#   i3:    bindsym $mod+d exec --no-startup-id ~/.config/rofi-spotlight/launch
#   sway:  bindsym $mod+d exec ~/.config/rofi-spotlight/launch
#   XFCE:  xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Primary><Alt>r' -n -t string -s "$HOME/.config/rofi-spotlight/launch"
```

`launch` runs rofi with `-no-config -theme spotlight.rasi`, so it's isolated from the global rofi config and resolves its script paths from its own location at runtime (rofi doesn't expand `~`/`$HOME` in mode paths, so they can't live in a theme file). If `colors-wal.rasi` exists beside it, `launch` layers that palette on top of the built-in Catppuccin defaults — so a missing palette file never breaks the launcher, it just falls back to the defaults.

**Dependencies:** `rofi`, `python3`, `xdg-utils` (`xdg-open`), `util-linux` (`setsid`), and an icon theme — `Papirus-Dark` by default; change `icon-theme` in `spotlight.rasi` to one you have.

## Files

- `launch`: portable, self-contained entry point. Bind your hotkey to this.
- `spotlight.rasi`: rofi options + Spotlight-style theme, **with the default Catppuccin palette baked in** (`@bg`/`@fg`/`@accent`/`@sel-fg`). Loaded only via `launch` (`-theme`), never installed as the global config.
- `colors-wal.rasi`: **optional** palette override, layered by `launch` when present. A symlink to the pywal output, or a copy of `colors-wal.rasi.example`. Git-ignored (per-machine); absent = built-in defaults.
- `templates/colors-rofi-spotlight.rasi`: pywal template → `~/.cache/wal/colors-rofi-spotlight.rasi`. Change the color indices (`color1`..`color6`) for a different accent.
- `colors-wal.rasi.example`: a ready-to-edit override palette (defines the 4 vars); copy to `colors-wal.rasi` and tweak for a custom static theme.
- `scripts/files.sh`: file list mode. As `files-quick.sh` (symlink) it lists everyday files for the main box; as `files.sh` it's the lazy deep-search tab.
- `scripts/web.sh`: receives unmatched text → opens URL or Google search in the default browser.

## Notes / gotchas

- Fonts use the generic `sans-serif` alias → whatever your system's default sans is. Change `font` in `spotlight.rasi` for a specific face.
- The frosted `bg` alpha only shows with a running compositor (picom, etc.); without one it renders opaque.
- rofi loads **every** mode at startup, so the deep tab only shows a "Load all files" entry until Enter — otherwise the main box takes ~0.7s to open.
- Keep `listview { fixed-height: true; }`; with `false` rofi measures every row (1.7s with many files).
- Don't enable `drun-use-desktop-cache`: it keeps showing uninstalled apps and only saves ~8ms.
- Rofi's theme parser misreads a quoted string followed by another quoted value in the same block, so `entry` properties are split over several blocks.
- Opening uses `xdg-open`; a file type with no default app opens nothing (`xdg-mime default <app>.desktop <mime>`).
- The `src`/`lib`/`jdk*`/`netbeans*` prune names in `files.sh` just trim noise; harmless if you don't have them.
