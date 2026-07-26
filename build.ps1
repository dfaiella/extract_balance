$ErrorActionPreference = 'Stop'

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootDir

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error 'uv is required. Install it first: https://docs.astral.sh/uv/'
    exit 1
}

uv sync --extra dev
uv run pytest
uv run pyinstaller --onefile --name account-balance-viewer --distpath dist --workpath build --specpath build src/extract_account_balance/__main__.py
