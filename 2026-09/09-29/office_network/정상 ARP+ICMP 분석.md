## 정상 ARP/ICMP 분석

### 테스트

DEV-PC1에서 OPS-PC1로 Ping 수행

- Source: 192.168.10.10
- Destination: 192.168.20.10

### ARP 분석

DEV-PC1과 OPS-PC1은 서로 다른 네트워크에 속한다.

DEV-PC1은 패킷을 기본 게이트웨이인
192.168.10.1로 전달하기 위해 Gateway의 MAC 주소를 확인한다.

ARP Request는 Broadcast이므로 VLAN 10 내부의
DEV-PC2, Server, L3 Switch 방향으로 전달된다.

192.168.10.1을 가진 L3 Switch가 ARP Reply를 반환한다.

### ICMP 분석

ARP 과정 이후 ICMP Echo Request가 다음 경로로 전달된다.

DEV-PC1
→ L2 SW-A
→ L3 SWITCH
→ L2 SW-B
→ OPS-PC1

L3 Switch의 Inter-VLAN Routing을 통해
VLAN 10에서 VLAN 20으로 패킷이 정상 전달되는 것을 확인하였다.