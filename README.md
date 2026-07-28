# extract_account_balance

A small offline desktop app for loading account statement PDFs, calculating
daily and monthly account balances, and retaining transaction history between
runs.

## Features

- Drag and drop a PDF file into the window or use the button to browse.
- Reads PDF text with an offline reader backend that prefers PyMuPDF and falls back to pypdf.
- Extracts transaction dates, amounts, details, and resulting account balances
  from supported PDF rows.
- Saves imported statements as JSON and loads them again when the app starts.
- Keeps a backup copy of the history JSON and a simple activity log in the user data folder.
- The **Daily & Monthly Average** tab prominently displays the monthly average,
  lists newest days first, and plots daily balances with a rolling-average
  line.
- The **All Transactions** tab lists every extracted transaction, including
  same-day transactions, and plots every account balance in a bar chart.
- Money in tables and chart axes is formatted as currency.

## Monthly balance calculation

The app calculates the monthly average as:

```text
sum of each day's end-of-day account balance / number of days in the month
```

- When a date has multiple transactions, the last transaction is its
  end-of-day balance.
- A date with no transactions uses the next available account balance.
- If no later balance exists, the latest known balance is carried through the
  end of the month.
- Calendar month length is used, including February 29 in leap years.

## Saved data

An import is saved immediately, and history is saved again when the app closes.
The next launch automatically reloads the most recently viewed statement
history. Imported PDF copies, JSON history, backups, and the activity log are
kept in the application data directory:

- Windows: `%LOCALAPPDATA%\AccountBalanceViewer`
- macOS/Linux: `~/.account_balance_viewer`

The **Data** menu can open the data folder, transaction-history JSON, or
activity log. Re-import an older statement if it was saved before transaction
amounts and details were supported.

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
