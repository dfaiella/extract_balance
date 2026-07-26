# macOS setup and run guide

This guide is for a complete new macOS user who wants to develop and run the app locally.

## 1. One-time development environment setup

1. Install Python 3.11 or newer.
2. Install uv if it is not already available:

   ```bash
   brew install uv
   ```

3. Open Terminal in the project folder:

   ```bash
   cd /path/to/extract_account_balance
   ```

4. Create and activate the project environment:

   ```bash
   uv sync --extra dev
   ```

5. Confirm the app can be imported and the tests pass:

   ```bash
   uv run pytest
   ```

6. Install the project into the environment so the command-line entry points are available:

   ```bash
   uv pip install -e .
   ```

## 2. How to load and run the tool after installation

From the project folder, run either of these commands:

```bash
./run.sh
```

On Windows PowerShell, use:

```powershell
./run.ps1
```

or directly:

```bash
uv run python -m extract_account_balance
```

or, after installation, use the installed entry points:

```bash
uv run extract-account-balance
# or
uv run account-balance-viewer
```

## 3. Helpful notes for first-time use

- The app stores its JSON history and backup files in your home folder under `.account_balance_viewer`.
- Every time the history is saved, the app also writes a simple line to `activity.log` so you can track what changed.
- Drag and drop a PDF file onto the window, or use the Load PDF button.
