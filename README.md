# extract_account_balance

A small offline desktop app for loading account statement PDFs, extracting date/balance rows, storing them as JSON, and displaying them in a simple chart.

## Features

- Drag and drop a PDF file into the window or use the button to browse.
- Reads PDF text with an offline reader backend that prefers PyMuPDF and falls back to pypdf.
- Extracts simple date/balance rows from the PDF text.
- Saves rows as JSON for later use.
- Keeps a backup copy of the history JSON and a simple activity log in the user data folder.
- Displays a simple bar chart of date vs balance.

## Quick start

For macOS setup and first-run instructions, see [docs/mac-setup.md](docs/mac-setup.md).

## Development

If you push this repository to GitHub for the first time, Git may open a credential prompt. Leave that popup available and complete the sign-in so the push can proceed.

Install dependencies with uv:

```bash
uv sync --extra dev
```

Run tests:

```bash
uv run pytest
```

Run the desktop app from the project checkout:

```bash
uv run python -m extract_account_balance
```

Or use the helper scripts:

On macOS/Linux:

```bash
./build.sh
./run.sh
```

On Windows PowerShell:

```powershell
./build.ps1
./run.ps1
```

After installation, the app can also be launched with either of these commands:

```bash
uv run extract-account-balance
# or
uv run account-balance-viewer
```

Build a standalone executable:

```bash
./build.sh       # macOS/Linux
# .\build.ps1    # Windows PowerShell
```

On macOS, double-click `build-and-install-macos.command` to build, install, and open the latest app without setting up a PATH. See [the macOS build and distribution notes](docs/mac-setup.md#3-build-and-install-the-app-recommended). The executable must be built on macOS; standard desktop distribution uses a signed and notarized `.app` bundle, typically in a DMG.
