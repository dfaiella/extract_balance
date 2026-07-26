#!/usr/bin/env bash
# Double-click this file in Finder, or run it from Terminal, to build and install
# the latest version for the current macOS user.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLICATIONS_DIR="$HOME/Applications"
APP_NAME="Account Balance Viewer"

cd "$ROOT_DIR"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script can only build a macOS app."
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

mkdir -p "$APPLICATIONS_DIR"

echo "Preparing the app..."
uv sync --extra dev

echo "Building the latest version..."
uv run pyinstaller \
  --noconfirm \
  --windowed \
  --onedir \
  --name "$APP_NAME" \
  --distpath "$APPLICATIONS_DIR" \
  --workpath build \
  --specpath build \
  src/extract_account_balance/__main__.py

echo
echo "Done. The latest app is installed in:"
echo "$APPLICATIONS_DIR/$APP_NAME.app"
echo "You can now open it from Finder's Applications folder."
open "$APPLICATIONS_DIR/$APP_NAME.app"
