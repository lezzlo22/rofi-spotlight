# rofi-spotlight

Spotlight-style launcher for XFCE built on plain [rofi](https://github.com/davatorium/rofi) (tested with 1.7.5). No extra packages.

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
ln -s ~/Documents/Personal/rofi-spotlight ~/.config/rofi
xfconf-query -c xfce4-keyboard-shortcuts -p '/commands/custom/<Primary><Alt>r' -n -t string -s 'rofi -show combi'
```

`config.rasi` hardcodes `/home/lesley/.config/rofi/scripts/...` (rofi doesn't expand `~`/`$HOME` in mode paths) — change it on another user/machine.

## Files

- `config.rasi`: modes + Spotlight-style theme (centered box on the monitor with the mouse).
- `scripts/files.sh`: file list mode. Called as `files-quick.sh` (symlink) it lists everyday files for the main box; as `files.sh` it's the lazy deep-search tab.
- `scripts/web.sh`: lists nothing; receives unmatched text → opens URL or Google search in the default browser.

## Notes / gotchas

- rofi loads **every** mode at startup, so the deep tab only shows a "Load all files" entry until Enter — otherwise the main box takes ~0.7s to open.
- Keep `listview { fixed-height: true; }`; with `false` rofi measures every row (1.7s with many files).
- Don't enable `drun-use-desktop-cache`: it keeps showing uninstalled apps and only saves ~8ms.
- Rofi's theme parser misreads a quoted string followed by another quoted value in the same block, so `entry` properties are split over several blocks.
- Opening uses `xdg-open`; a file type with no default app opens nothing (`xdg-mime default <app>.desktop <mime>`).
