# Wi-Fi 연결 끊기
Disable-NetAdapter -Name "Wi-Fi" -Confirm:$false

# 10초 기다리기
Start-Sleep -Seconds 10

# Wi-Fi 다시 연결
Enable-NetAdapter -Name "Wi-Fi" -Confirm:$false

# 연결될 시간을 조금 기다리기
Start-Sleep -Seconds 5

# 네트워크 연결 확인
ping 8.8.8.8
