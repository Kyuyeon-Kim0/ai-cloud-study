# 기본 시스템 정보 조회
$cs = Get-CimInstance Win32_ComputerSystem          # 제조사, 모델, 전체 메모리 정보 조회
$os = Get-CimInstance Win32_OperatingSystem         # 운영체제, 메모리, 부팅 시각 조회
$cpu = Get-CimInstance Win32_Processor | Select-Object -First 1  # CPU 정보 조회
$c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"   # C드라이브 정보 조회

# 메모리 계산
$memTotalGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)     # 전체 메모리를 GB로 변환
$memFreeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 1)      # 남은 메모리를 GB로 변환
$memUsedGB = [math]::Round($memTotalGB - $memFreeGB, 1)          # 사용 중인 메모리 계산
$memUsePct = [math]::Round(($memUsedGB / $memTotalGB) * 100, 1)  # 메모리 사용률 계산

# C드라이브 계산
$cTotalGB = [math]::Round($c.Size / 1GB, 1)                       # C드라이브 전체 용량 계산
$cFreeGB = [math]::Round($c.FreeSpace / 1GB, 1)                  # C드라이브 남은 공간 계산
$cUsedGB = [math]::Round($cTotalGB - $cFreeGB, 1)                # C드라이브 사용량 계산

# 결과 출력
Write-Host "===== 내 PC 시스템 정보 ====="                        # 제목 출력
Write-Host "제조사 / 모델 : $($cs.Manufacturer) / $($cs.Model)"   # 제조사와 모델 출력
Write-Host "운영체제      : $($os.Caption)"                       # 운영체제 이름 출력
Write-Host "CPU           : $($cpu.Name)"                         # CPU 이름 출력
Write-Host "CPU 코어      : $($cpu.NumberOfCores)개"              # 물리 CPU 코어 수 출력
Write-Host "메모리        : $memUsedGB GB / $memTotalGB GB ($memUsePct%)"  # 메모리 상태 출력
Write-Host "C드라이브     : 사용 $cUsedGB GB / 전체 $cTotalGB GB / 남음 $cFreeGB GB"  # 디스크 상태 출력
Write-Host "최근 부팅     : $($os.LastBootUpTime)"                # 최근 부팅 시각 출력
