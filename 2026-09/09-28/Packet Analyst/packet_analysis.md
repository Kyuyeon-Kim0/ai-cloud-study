# 정상 패킷 분석

## 1. 정상 ICMP 분석

### 테스트

DEV-PC에서 SERVER로 Ping을 수행하였다.

- Source: 192.168.10.10
- Destination: 192.168.30.10

### 관찰 결과

ICMP Echo Request가 다음 경로로 전달되었다.

DEV-PC → SW1 → R1 → SW1 → SERVER

SERVER의 ICMP Echo Reply는 역방향으로 DEV-PC까지
정상적으로 반환되었다.

### Layer 3 분석

ICMP Echo Request에서 다음 정보를 확인하였다.

- Source IP: 192.168.10.10
- Destination IP: 192.168.30.10
- ICMP Type: 8 (Echo Request)

Router를 통과한 이후에도 Source IP와 Destination IP는
유지되었다.

단, Router를 통과하면서 TTL 값은 1 감소하였다.

### Layer 2 분석

Router의 In Layers와 Out Layers를 비교한 결과
Ethernet MAC 주소가 변경되는 것을 확인하였다.

이는 Router가 목적지 네트워크로 패킷을 전달하기 위해
다음 구간에서 사용할 새로운 Layer 2 Frame을 생성하기 때문이다.

### Routing 분석

Router에서 목적지 IP에 대한 경로가 존재하는 것을 확인하였다.

Router는 Routing Table을 기반으로 VLAN 30 방향으로
패킷을 전달했으며, 이 과정에서 TTL을 1 감소시켰다.

### 정상 판단

ICMP Echo Request와 Echo Reply가 정상적으로 왕복하였다.

따라서 VLAN 10과 VLAN 30 사이의 Layer 3 통신이
정상적으로 이루어지고 있음을 확인하였다.


## 2. 정상 ARP Request 분석

DEV-PC에서 SERVER로 최초 통신을 수행할 때
ARP Request가 발생하였다.

Packet Tracer에서 다음 정보를 확인하였다.

- Sender IP: 192.168.10.10
- Target IP: 192.168.10.1
- Source MAC: 0001.975D.8855
- Destination MAC: FFFF.FFFF.FFFF (Broadcast)

### 관찰 결과

DEV-PC와 SERVER는 서로 다른 네트워크에 존재한다.

따라서 DEV-PC는 SERVER(192.168.30.10)의 MAC 주소를
직접 조회하지 않았다.

대신 다른 네트워크로 패킷을 전달하기 위해
Default Gateway인 192.168.10.1의 MAC 주소를 조회하였다.

DEV-PC는 Gateway의 MAC 주소를 알지 못했기 때문에
ARP Request를 FFFF.FFFF.FFFF로 Broadcast하였다.

### Switch에서의 전달

ARP Request는 SW1의 Fa0/1으로 들어왔다.

SW1은 VLAN 10의 ARP Broadcast를 처리하고,
Gi0/1 Trunk를 통해 VLAN 10의 ARP를 R1 방향으로 전달하였다.

### 정상 판단

Gateway를 대상으로 ARP Request가 발생하고,
이후 Gateway의 ARP Reply가 반환되는 것을 확인하였다.

따라서 DEV-PC가 Default Gateway의 MAC 주소를
정상적으로 획득할 수 있는 상태이다.


## VLAN 장애 ARP 분석

### 장애 설정

DEV-PC가 연결된 SW1의 Fa0/1을
VLAN 10에서 VLAN 20으로 잘못 변경하였다.

- DEV-PC IP: 192.168.10.10
- Default Gateway: 192.168.10.1
- 정상 VLAN: VLAN 10
- 장애 VLAN: VLAN 20

### 패킷 관찰

DEV-PC는 Default Gateway의 MAC 주소를 확인하기 위해
ARP Request를 발생시켰다.

- Sender IP: 192.168.10.10
- Target IP: 192.168.10.1
- Destination MAC: FFFF.FFFF.FFFF (Broadcast)

ARP Request 자체의 IP 정보는 정상 상태와 동일하였다.

하지만 SW1의 Fa0/1이 VLAN 20으로 설정되어 있었기 때문에
해당 ARP Broadcast는 VLAN 20의 프레임으로 처리되었다.

SW1에서 Router0 방향으로 전달될 때
802.1Q(Dot1Q) VLAN 태그가 포함된 것을 확인하였다.

### Router 분석

Router0는 해당 ARP 프레임을 VLAN 20 트래픽으로 수신하였다.

그러나 ARP의 Target IP는 VLAN 10의 Gateway인
192.168.10.1이었다.

Router의 VLAN 20 Gateway는 192.168.20.1이므로
192.168.10.1에 대한 정상적인 ARP Reply가 발생하지 않았다.

### 장애 판단

DEV-PC의 IP 설정은 VLAN 10 대역이지만
Switch Access Port는 VLAN 20에 속해 있었다.

따라서 Layer 2 VLAN과 Layer 3 IP 네트워크가
서로 일치하지 않는 VLAN 불일치 장애로 판단할 수 있다.

ARP 단계에서 Default Gateway의 MAC 주소를 획득하지 못하므로
이후 정상적인 ICMP 통신도 진행할 수 없다.