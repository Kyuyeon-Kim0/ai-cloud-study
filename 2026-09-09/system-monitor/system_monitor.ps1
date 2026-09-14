$ErrorActionPreference = "Stop"

function Get-StatusLabel {
    param(
        [double]$Value,
        [double]$Warning,
        [double]$Critical,
        [switch]$LowerIsWorse
    )

    if ($LowerIsWorse) {
        if ($Value -le $Critical) { return "위험" }
        if ($Value -le $Warning) { return "주의" }
        return "정상"
    }

    if ($Value -ge $Critical) { return "위험" }
    if ($Value -ge $Warning) { return "주의" }
    return "정상"
}

function Format-Gb {
    param([double]$Value)

    $rounded = [math]::Round($Value, 1)
    if ($rounded -eq [math]::Round($rounded, 0)) {
        return ([int]$rounded).ToString()
    }

    return $rounded.ToString("0.0")
}

$cpuLoad = [math]::Round((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average, 0)
$os = Get-CimInstance Win32_OperatingSystem
$cDrive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"

$memTotalGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$memFreeGb = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
$memUsedGb = [math]::Round($memTotalGb - $memFreeGb, 1)
$memUsePct = [math]::Round(($memUsedGb / $memTotalGb) * 100, 0)

$cTotalGb = [math]::Round($cDrive.Size / 1GB, 0)
$cFreeGb = [math]::Round($cDrive.FreeSpace / 1GB, 0)
$cUsedGb = [math]::Round($cTotalGb - $cFreeGb, 0)
$cFreePct = [math]::Round(($cFreeGb / $cTotalGb) * 100, 0)

$cpuStatus = Get-StatusLabel -Value $cpuLoad -Warning 70 -Critical 90
$memStatus = Get-StatusLabel -Value $memUsePct -Warning 75 -Critical 90
$diskStatus = Get-StatusLabel -Value $cFreePct -Warning 20 -Critical 10 -LowerIsWorse

$topProcesses = Get-Process |
    Where-Object { $_.WorkingSet64 -gt 0 } |
    Sort-Object WorkingSet64 -Descending |
    Select-Object -First 3

$overallStatus = if (@($cpuStatus, $memStatus, $diskStatus) -contains "위험") {
    "위험"
} elseif (@($cpuStatus, $memStatus, $diskStatus) -contains "주의") {
    "주의"
} else {
    "정상"
}

$insights = @()
$actions = @()

if ($cpuStatus -eq "정상") { $insights += "CPU 여유 있음" } else { $insights += "CPU 사용률 확인 필요"; $actions += "CPU 사용량이 높은 프로세스 확인" }
if ($memStatus -eq "정상") { $insights += "메모리 여유 있음" } else { $insights += "메모리 사용량 확인 필요"; $actions += "불필요한 프로그램 종료 검토" }
if ($diskStatus -eq "정상") { $insights += "디스크 공간 충분" } else { $insights += "디스크 여유 공간 부족"; $actions += "불필요한 파일 정리 검토" }

if ($overallStatus -eq "정상") {
    $insights += "현재 병목 없음"
    $actions += "현재 조치 필요 없음"
}

Write-Host "===== PC Performance Agent ====="
Write-Host ""
Write-Host "[시스템]"
Write-Host ("CPU     : {0}%        {1}" -f $cpuLoad, $cpuStatus)
Write-Host ("메모리  : {0} / {1} GB ({2}%)   {3}" -f (Format-Gb $memUsedGb), (Format-Gb $memTotalGb), $memUsePct, $memStatus)
Write-Host ("C드라이브: {0} / {1} GB" -f $cUsedGb, $cTotalGb)
Write-Host ("남은 공간: {0} GB    {1}" -f $cFreeGb, $diskStatus)
Write-Host ""
Write-Host "[상위 프로세스]"
for ($i = 0; $i -lt $topProcesses.Count; $i++) {
    $process = $topProcesses[$i]
    $memoryGb = [math]::Round($process.WorkingSet64 / 1GB, 1)
    Write-Host ("{0}. {1,-14} {2} GB" -f ($i + 1), ($process.ProcessName + ".exe"), (Format-Gb $memoryGb))
}
Write-Host ""
Write-Host "[판단]"
Write-Host "전체 시스템 상태: $overallStatus"
Write-Host ""
Write-Host "[인사이트]"
foreach ($insight in $insights) {
    Write-Host "- $insight"
}
Write-Host ""
Write-Host "[조치사항]"
foreach ($action in $actions) {
    Write-Host "- $action"
}