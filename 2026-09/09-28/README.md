# 2026-09-28 (월) 학습 기록

## 학습 주제

- Cisco Packet Tracer를 이용한 사내 네트워크 토폴로지 설계
- VLAN으로 개발·운영·서버 네트워크 분리
- 802.1Q Trunk와 Router-on-a-Stick을 이용한 VLAN 간 라우팅
- 정상 ICMP·ARP 패킷의 L2/L3 동작 분석
- VLAN과 IP 대역이 일치하지 않을 때 발생하는 ARP 통신 장애 분석

## 핵심 이해

### VLAN과 Router-on-a-Stick

- VLAN은 하나의 스위치에서 논리적으로 분리된 네트워크를 구성한다.
- 액세스 포트는 하나의 VLAN에 속하며, Trunk 포트는 802.1Q 태그로 여러 VLAN의 트래픽을 전달한다.
- Router-on-a-Stick은 라우터의 하나의 물리 인터페이스를 VLAN별 서브인터페이스로 나누어, 서로 다른 VLAN 사이를 라우팅하는 방식이다.
- 서로 다른 VLAN 간 통신에는 각 VLAN의 기본 게이트웨이와 라우팅이 필요하다.

### 패킷 흐름 분석

- DEV-PC에서 다른 VLAN의 SERVER로 Ping을 보낼 때 IP 패킷은 유지되지만, 라우터를 지날 때 Ethernet MAC 주소는 다음 구간에 맞게 바뀐다.
- 라우터는 패킷을 전달할 때 TTL을 1 감소시킨다.
- 다른 IP 네트워크로 처음 통신하는 호스트는 목적지 서버의 MAC 주소가 아니라 기본 게이트웨이의 MAC 주소를 ARP로 조회한다.
- ARP Request는 브로드캐스트 MAC 주소 `FFFF.FFFF.FFFF`로 같은 VLAN 안에 전달된다.

### VLAN 불일치 장애

- 호스트 IP가 VLAN 10 대역이어도, 연결된 스위치 액세스 포트가 VLAN 20으로 설정되면 VLAN과 IP 네트워크가 불일치한다.
- 이 경우 호스트는 VLAN 10 게이트웨이의 MAC 주소를 ARP로 요청하지만, 프레임은 VLAN 20으로 전달되어 올바른 ARP Reply를 받지 못한다.
- 장애 분석은 IP 설정뿐 아니라 스위치 포트 VLAN, Trunk 허용 VLAN, 게이트웨이 서브인터페이스를 함께 확인해야 한다.

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [Network Architect/](<Network Architect/>) | VLAN 10·20·30, Trunk, Router-on-a-Stick으로 구성한 정상 기준 네트워크 |
| [네트워크 설계 명세](<Network Architect/network_spec.md>) | 토폴로지, IP/VLAN 주소 계획, 포트 및 게이트웨이 구성, 정상 통신 결과 |
| [정상 토폴로지 이미지](<Network Architect/topology.PNG>) | PacketLab 사내 네트워크 구성 화면 |
| [Packet Analyst/](<Packet Analyst/>) | 정상 패킷과 VLAN 장애 패킷을 비교하는 분석 자료 |
| [패킷 분석 기록](<Packet Analyst/packet_analysis.md>) | ICMP·ARP 정상 흐름과 VLAN 불일치 장애 원인 분석 |
| [정상 네트워크 패킷 파일](<Packet Analyst/office_network_normal.pkt>) | 정상 상태 패킷 관찰용 Packet Tracer 파일 |
| [VLAN 장애 패킷 파일](<Packet Analyst/fault_vlan.pkt>) | 액세스 포트 VLAN 오설정 장애 재현용 Packet Tracer 파일 |
| [ARP Request 캡처](<Packet Analyst/arp request.png>) | 기본 게이트웨이를 대상으로 한 ARP Broadcast |

## 네트워크 구성 요약

| 장비 | VLAN | IP 주소 | 기본 게이트웨이 |
| --- | ---: | --- | --- |
| DEV-PC | 10 | `192.168.10.10/24` | `192.168.10.1` |
| OPS-PC | 20 | `192.168.20.10/24` | `192.168.20.1` |
| SERVER | 30 | `192.168.30.10/24` | `192.168.30.1` |

스위치 `SW1`의 `Gi0/1`과 라우터 `R1`의 `Gi0/0`은 Trunk로 연결한다. 라우터에는 `Gi0/0.10`, `Gi0/0.20`, `Gi0/0.30` 서브인터페이스를 구성해 각 VLAN의 게이트웨이 역할을 맡긴다.

## 실습 순서

1. [Network Architect/office_network.pkt](<Network Architect/office_network.pkt>)를 Cisco Packet Tracer에서 열고 토폴로지와 장비 설정을 확인한다.
2. DEV-PC에서 `ping 192.168.30.10`을 실행해 VLAN 10과 VLAN 30 사이의 정상 통신을 확인한다.
3. Simulation 모드에서 ICMP Echo Request/Reply의 IP, MAC 주소와 TTL 변화를 관찰한다.
4. [Packet Analyst/office_network_normal.pkt](<Packet Analyst/office_network_normal.pkt>)에서 최초 통신의 ARP Request와 ARP Reply를 확인한다.
5. [Packet Analyst/fault_vlan.pkt](<Packet Analyst/fault_vlan.pkt>)에서 DEV-PC 포트의 VLAN을 확인하고, ARP Request가 어느 VLAN 태그로 전달되는지 정상 상태와 비교한다.
6. 장애 상태의 액세스 포트를 VLAN 10으로 되돌린 뒤, 게이트웨이 ARP와 ICMP 통신이 복구되는지 확인한다.

## 준비물

- Cisco Packet Tracer
- `.pkt` 파일을 열 수 있는 Cisco 계정 또는 설치 환경
- 패킷 상세 정보를 확인할 수 있는 Simulation 모드
