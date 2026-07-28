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

## 3. Build and install the app (recommended)

For the simplest repeatable workflow, double-click `build-and-install-macos.command` in Finder. The first time, macOS may ask which app should open it; choose Terminal.

The script prepares the project, builds the latest desktop app, installs it in your personal Applications folder, and opens it. Run the same file again whenever you want to build a newer version. No PATH setup or separate installation step is needed.

The installed app is here:

```text
~/Applications/Account Balance Viewer.app
```

You can open it later from Finder by choosing **Go → Home**, then opening `Applications`.

If Finder says it cannot run the file, open Terminal in the project folder once and run:

```bash
chmod +x build-and-install-macos.command
```

## 4. Build a standalone macOS executable

Build on the Mac and processor architecture that will run the app. PyInstaller executables are platform-specific; a binary built on Windows will not run on macOS.

From the project folder, run:

```bash
./build.sh
```

The script installs the development dependencies, runs the tests, and writes the executable here:

```text
dist/account-balance-viewer
```

Launch the built executable with:

```bash
./dist/account-balance-viewer
```

If macOS reports that `build.sh` is not executable, grant permission once and rerun it:

```bash
chmod +x build.sh
./build.sh
```

## 5. Installing and distributing on macOS

The current build produces a standalone executable launched from Terminal. It can be copied to a directory on the user's `PATH` (for example, `/usr/local/bin`) if that workflow is useful, but it is not the usual installation experience for a desktop GUI app.

The usual macOS distribution is a signed and notarized `.app` bundle, often delivered in a `.dmg` disk image. The user opens the disk image and drags the app to `/Applications`. The simple local-build script above produces an unsigned `.app` bundle for the current user; for sharing with other users, use the signed release format described below.

Keep the build script focused on creating and testing the artifact. When the app is ready to distribute, add a separate macOS packaging script or CI release workflow that:

1. Builds an `.app` bundle with PyInstaller on macOS.
2. Codesigns it with an Apple Developer ID certificate.
3. Notarizes and staples it with Apple.
4. Creates a `.dmg` containing the app and an `/Applications` shortcut.

That release artifact is what users should install; a local development build normally does not need an install script.

## 6. Helpful notes for first-time use

- The app stores its JSON history and backup files in your home folder under `.account_balance_viewer`.
- Imported statements are saved immediately, saved again at shutdown, and
  loaded automatically the next time the app starts.
- Every time the history is saved, the app also writes a simple line to `activity.log` so you can track what changed.
- Drag and drop a PDF file onto the window, or use the Load PDF button.
- Use **Daily & Monthly Average** for the monthly summary, daily balances, and
  rolling-average chart. Use **All Transactions** to see every transaction's
  date, amount, resulting account balance, details, and chart bar.
