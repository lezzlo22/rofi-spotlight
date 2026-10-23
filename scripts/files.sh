#!/bin/sh
# rofi script mode: list files/folders under ~ for live filtering; open the picked one.
# As files-quick.sh: everyday files only (depth 5, no code internals), shown in the main box.
# As files.sh (Ctrl+Tab tab): rofi loads every tab at startup, so the full list only loads after "Load all files".
list() {
    set -f  # keep the * in $extra literal for find
    # shellcheck disable=SC2086
    find "$HOME" -mindepth 1 $depth \( -name '.*' -o -name node_modules -o -name __pycache__ -o -name build \
        -o -name dist -o -name target -o -name venv -o -name site-packages -o -name CPM_modules \
        -o -name vendor -o -path "$HOME/go" -o -path "$HOME/snap" $extra \) -prune \
        -o -type d -printf '%P\0icon\037folder\n' -o -printf '%P\0icon\037text-x-generic\n'
}
case "$0" in
    *quick*) depth="-maxdepth 5"
             # ponytail: name heuristics keep this ~9k entries; rofi load time grows with entry count
             extra="-o -name src -o -name lib -o -name include -o -name test -o -name tests -o -name public
                    -o -name assets -o -name components -o -path $HOME/jdk* -o -path $HOME/netbeans*
                    -o -path $HOME/Java_ME* -o -path $HOME/Documents/Personal/jdk* -o -path $HOME/Documents/Personal/WTK" ;;
    *) depth=""; extra="" ;;
esac
if { [ "$ROFI_RETV" = 1 ] && [ "$ROFI_INFO" = LOAD ]; } || { [ "$ROFI_RETV" = 2 ] && [ -z "$depth" ]; }; then
    printf '\0message\037All files under ~ — type to filter\n'
    list
elif [ "$ROFI_RETV" = 1 ]; then
    setsid -f xdg-open "$HOME/$1" >/dev/null 2>&1
elif [ "$depth" ]; then
    list
else
    printf '\0message\037Deep search: press Enter to load every file under ~ (~2s), then type\n'
    printf 'Load all files\0icon\037system-search\037info\037LOAD\n'
fi
