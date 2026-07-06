#!/usr/bin/env sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v pwsh >/dev/null 2>&1; then
  exec pwsh -NoProfile -ExecutionPolicy Bypass -File "$SCRIPT_DIR/new-indicator-workspace.ps1" -Destination "$1" -Arity "$2" -ClassName "$3"
fi

if command -v powershell >/dev/null 2>&1; then
  exec powershell -NoProfile -ExecutionPolicy Bypass -File "$SCRIPT_DIR/new-indicator-workspace.ps1" -Destination "$1" -Arity "$2" -ClassName "$3"
fi

echo "PowerShell is required to run new-indicator-workspace.ps1. Use the packaged assets directly if neither pwsh nor powershell is available." >&2
exit 127
