Write-Host "안녕하세요!"
Write-Host "PowerShell 공부를 시작합니다."

$name = "김규연"
Write-Host "안녕하세요, $name 님!"

$name = Read-Host "이름을 입력하세요"
Write-Host "반갑습니다, $name 님!"

Write-Host "현재 폴더의 파일입니다."
Get-ChildItem
Write-Host "끝!"