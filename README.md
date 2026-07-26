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
uv run pyinstaller --onefile --name account-balance-viewer --distpath dist --workpath build --specpath build src/extract_account_balance/__main__.py
```
