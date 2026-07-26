$ErrorActionPreference = 'Stop'

$rootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $rootDir

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Error 'uv is required. Install it first: https://docs.astral.sh/uv/'
    exit 1
}

uv run python -m extract_account_balance
