#!/bin/sh
# rofi script mode: lists nothing; text that matches nothing lands here -> open URL or web search
[ -z "$1" ] && exit 0
if printf '%s' "$1" | grep -qE '^(https?://)?[^ ]+\.[a-z]{2,}(/[^ ]*)?$'; then
    url="$1"; case "$url" in http*) ;; *) url="https://$url" ;; esac
else
    url="https://www.google.com/search?q=$(python3 -c 'import sys,urllib.parse;print(urllib.parse.quote_plus(sys.argv[1]))' "$1")"
fi
setsid -f xdg-open "$url" >/dev/null 2>&1
