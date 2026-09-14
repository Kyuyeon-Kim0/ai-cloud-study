$ErrorActionPreference = 'Stop'

$now = Get-Date
$wallpaper = if ($now.Hour -lt 12) {
    (Join-Path $PSScriptRoot 'am.png')
} else {
    (Join-Path $PSScriptRoot 'pm.png')
}

if (-not (Test-Path -LiteralPath $wallpaper -PathType Leaf)) {
    throw "Wallpaper file not found: $wallpaper"
}

Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class WallpaperApi {
    [DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    public static extern bool SystemParametersInfo(uint action, uint param, string vParam, uint winIni);
}
'@

$success = [WallpaperApi]::SystemParametersInfo(20, 0, $wallpaper, 3)
if (-not $success) {
    $errorCode = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    throw "SystemParametersInfo failed with Win32 error $errorCode"
}

Add-Content -LiteralPath (Join-Path $PSScriptRoot 'wallpaper.log') -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') Applied $wallpaper"
