#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. Install it first: https://docs.astral.sh/uv/" >&2
  exit 1
fi

uv sync --extra dev
uv run pytest
uv run pyinstaller --onefile --name account-balance-viewer --distpath dist --workpath build --specpath build src/extract_account_balance/__main__.py
