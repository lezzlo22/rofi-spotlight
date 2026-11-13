#!/bin/sh
# Custom input handler for the combined mode.
exec python3 "$(dirname -- "$0")/actions.py" "$@"
