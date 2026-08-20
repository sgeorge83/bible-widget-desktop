# Build Store-ready payload + MSIX for Bible Widget Desktop
# Usage (from repo root):
#   powershell -ExecutionPolicy Bypass -File packaging\build_msix.ps1
# Optional:
#   -IdentityName WordOnAirLabs.BibleWidgetDesktop
#   -Publisher "CN=YOUR-PARTNER-CENTER-ID"
#   -Version 1.0.0.0

param(
    [string]$IdentityName = "",
    [string]$Publisher = "",
    [string]$Version = "1.0.0.0"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = (Get-Location).Path }
Set-Location $Root

Write-Host "Generating Store assets..."
python packaging\generate_assets.py

Write-Host "Building PyInstaller payload..."
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean bible-widget-desktop.spec

$Payload = Join-Path $Root "dist\BibleWidgetDesktop"
if (-not (Test-Path (Join-Path $Payload "BibleWidgetDesktop.exe"))) {
    throw "PyInstaller output missing: $Payload\BibleWidgetDesktop.exe"
}

Copy-Item (Join-Path $Root "packaging\AppxManifest.xml") (Join-Path $Payload "AppxManifest.xml") -Force
$AssetsDest = Join-Path $Payload "Assets"
New-Item -ItemType Directory -Force -Path $AssetsDest | Out-Null
Copy-Item (Join-Path $Root "packaging\Assets\*") $AssetsDest -Force

$manifestPath = Join-Path $Payload "AppxManifest.xml"
[xml]$manifest = Get-Content $manifestPath
if ($IdentityName) { $manifest.Package.Identity.Name = $IdentityName }
if ($Publisher) { $manifest.Package.Identity.Publisher = $Publisher }
if ($Version) { $manifest.Package.Identity.Version = $Version }
$manifest.Save($manifestPath)

$MsixDir = Join-Path $Root "dist"
$MsixPath = Join-Path $MsixDir "BibleWidgetDesktop_1.0.0.0_x64.msix"

$makeAppx = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\makeappx.exe" -ErrorAction SilentlyContinue |
    Sort-Object FullName -Descending |
    Select-Object -First 1

if ($makeAppx) {
    Write-Host "Packing MSIX with $($makeAppx.FullName)"
    & $makeAppx.FullName pack /d $Payload /p $MsixPath /o
    Write-Host "MSIX ready: $MsixPath"
} else {
    Write-Warning "makeappx.exe not found. Payload is ready at $Payload"
    Write-Warning "Install the Windows SDK, or pack this folder with the MSIX Packaging Tool, then upload to Partner Center."
}

Write-Host "Done. Next: Partner Center → Packages → upload the .msix (Store will sign it)."
