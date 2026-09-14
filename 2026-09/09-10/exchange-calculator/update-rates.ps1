param([string]$OutputDirectory = (Join-Path $PSScriptRoot 'data'))
$ErrorActionPreference = 'Stop'
$url = 'https://api.frankfurter.dev/v1/latest?from=USD&to=KRW,JPY,EUR'
$data = Invoke-RestMethod -Uri $url -TimeoutSec 30
if ($data.base -ne 'USD' -or $data.amount -ne 1) { throw 'Unexpected base currency or amount.' }
$date = [datetime]::ParseExact($data.date, 'yyyy-MM-dd', [cultureinfo]::InvariantCulture)
$fetched = [datetime]::UtcNow.ToString('o')
$rows = foreach ($currency in @('KRW', 'JPY', 'EUR')) {
    $rate = [double]$data.rates.$currency
    if ($rate -le 0 -or [double]::IsNaN($rate) -or [double]::IsInfinity($rate)) { throw "Invalid rate: $currency" }
    [pscustomobject][ordered]@{
        date = $date.ToString('yyyy-MM-dd')
        base = 'USD'
        currency = $currency
        rate = $rate.ToString('R', [cultureinfo]::InvariantCulture)
        fetched_at_utc = $fetched
        source = $url
    }
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$path = Join-Path $OutputDirectory 'exchange-rates.csv'
$temporary = Join-Path $OutputDirectory ([guid]::NewGuid().ToString() + '.tmp')
try {
    $rows | Export-Csv -LiteralPath $temporary -NoTypeInformation -Encoding UTF8
    Move-Item -LiteralPath $temporary -Destination $path -Force
} finally {
    if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
}
Write-Output "Saved: $path"
$rows | Format-Table date, base, currency, rate
