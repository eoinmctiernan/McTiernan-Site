param()

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$scriptPath = Join-Path $projectRoot 'scripts\update_media.py'

if (-not (Test-Path $scriptPath)) {
    Write-Error "Missing $scriptPath"
    exit 1
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Error "Python is not available in PATH. Install Python or run the script manually."
    exit 1
}

& $python.Source $scriptPath
exit $LASTEXITCODE
