# Office Network 구축 기록

## 1. 네트워크 구성

- L3 Switch: 1대
- L2 Switch: 2대
- DEV-PC: 2대
- OPS-PC: 2대
- DNS/Web Server: 1대

## 2. VLAN 구성

| VLAN | 용도 | Network | Gateway |
|---|---|---|---|
| VLAN 10 | 개발팀 DEV | 192.168.10.0/24 | 192.168.10.1 |
| VLAN 20 | 운영팀 OPS | 192.168.20.0/24 | 192.168.20.1 |

## 3. IP 구성

| 장비 | VLAN | IP | Gateway | DNS |
|---|---|---|---|---|
| DEV-PC1 | 10 | 192.168.10.10 | 192.168.10.1 | 192.168.10.100 |
| DEV-PC2 | 10 | 192.168.10.20 | 192.168.10.1 | 192.168.10.100 |
| Server | 10 | 192.168.10.100 | 192.168.10.1 | 192.168.10.100 |
| OPS-PC1 | 20 | 192.168.20.10 | 192.168.20.1 | 192.168.10.100 |
| OPS-PC2 | 20 | 192.168.20.20 | 192.168.20.1 | 192.168.10.100 |

## 4. L3 Switch 구성

- VLAN 10 DEV 생성
- VLAN 20 OPS 생성
- VLAN 10 Gateway: 192.168.10.1
- VLAN 20 Gateway: 192.168.20.1
- Inter-VLAN Routing 활성화
- L2 Switch 연결 포트 Trunk 구성
- VLAN 10, 20 Trunk 허용

## 5. L2 Switch 구성

### L2 SW-A
- DEV-PC1: VLAN 10
- DEV-PC2: VLAN 10
- Server: VLAN 10

### L2 SW-B
- OPS-PC1: VLAN 20
- OPS-PC2: VLAN 20

## 6. 통신 테스트

### DEV-PC → VLAN 10 Gateway

- 대상: 192.168.10.1
- Sent: 4
- Received: 4
- Loss: 0%
- 결과: 성공

### VLAN 10 → VLAN 20

- 대상: 192.168.20.10
- ICMP Echo Reply 정상 수신
- Inter-VLAN Routing 동작 확인
- 결과: 성공

### PC → Server

- 대상: 192.168.10.100
- Sent: 4
- Received: 4
- Loss: 0%
- 결과: 성공

### PC 간 통신

- 대상: 192.168.10.10
- Sent: 4
- Received: 4
- Loss: 0%
- 결과: 성공

## 7. 현재 상태

- VLAN 10 DEV 구성 완료
- VLAN 20 OPS 구성 완료
- Trunk 구성 완료
- L3 Switch Inter-VLAN Routing 구성 완료
- VLAN 간 통신 확인 완료
- Server 통신 확인 완료

네트워크 기본 구성 정상 동작 확인.

## 7. 현재 상태

VLAN 10 / VLAN 20 구성 및 Inter-VLAN Routing 동작 확인 완료.

Server 통신은 추가 점검이 필요한 상태.

## 8. 향후 분석 항목

- ARP
- ICMP
- DNS
- TCP/HTTP