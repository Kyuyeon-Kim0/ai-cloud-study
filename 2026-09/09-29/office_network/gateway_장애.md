## 정상 상태

DEV-PC1(192.168.10.10)과
OPS-PC1(192.168.20.10) 간 통신을 테스트하였다.

정상 Gateway:
- VLAN 10: 192.168.10.1
- VLAN 20: 192.168.20.1

ARP를 통해 Gateway의 MAC 주소를 확인한 후
ICMP Echo Request/Reply가 정상적으로 전달되었다.


## 장애 상태

OPS-PC1의 Gateway를 의도적으로 변경하였다.

정상:
192.168.20.1

장애:
192.168.20.254

OPS-PC1은 다른 네트워크로 패킷을 보내기 위해
192.168.20.254의 MAC 주소를 ARP로 요청하였다.

그러나 해당 IP를 사용하는 Gateway가 존재하지 않아
ARP Reply를 받지 못했고 ICMP 패킷 전달도 진행되지 않았다.


## 정상 / 장애 비교

| 항목 | 정상 | Gateway 장애 |
|---|---|---|
| ARP Request | 발생 | 발생 |
| ARP Target | 192.168.20.1 | 192.168.20.254 |
| ARP Reply | 있음 | 없음 |
| ICMP Request 전달 | 성공 | 실패 |
| ICMP Reply | 있음 | 없음 |
| 최종 결과 | Ping 성공 | Ping 실패 |