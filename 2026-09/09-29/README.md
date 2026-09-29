# 2026-09-29 (화) 학습 기록

## 학습 주제

- L3 스위치 기반 VLAN 10·20 사내 네트워크 구성
- Inter-VLAN Routing과 Trunk를 이용한 부서 간 통신
- ARP, ICMP, DNS, TCP/HTTP 순서의 정상 패킷 흐름 분석
- 잘못된 기본 게이트웨이, DNS 서비스 중지, HTTP 서비스 중지 장애 비교
- Cisco Packet Tracer와 Wireshark에서 정상·장애 패킷을 관찰하는 방법

## 핵심 이해

### Office Network 구조

- VLAN 10(개발팀)과 VLAN 20(운영팀)을 분리하고, L3 스위치의 SVI가 각각 `192.168.10.1`, `192.168.20.1` 기본 게이트웨이 역할을 한다.
- L2 스위치와 L3 스위치 사이의 Trunk는 여러 VLAN 트래픽을 전달하며, L3 스위치의 Inter-VLAN Routing이 서로 다른 VLAN 간 패킷을 라우팅한다.
- DNS와 웹 서버는 VLAN 10의 `192.168.10.100`에 배치되어 이름 해석과 HTTP 서비스를 제공한다.

### 패킷으로 장애 범위 좁히기

- 다른 네트워크로 통신하기 전에는 기본 게이트웨이의 MAC 주소를 알아내기 위해 ARP Request/Reply가 먼저 발생한다.
- 정상 상태에서는 ARP Reply, ICMP Echo Reply, DNS Response처럼 요청 뒤에 대응하는 응답이 이어진다.
- Gateway 장애에서는 존재하지 않는 게이트웨이를 대상으로 한 ARP Request만 보이고 ARP Reply가 없어 다른 VLAN으로 ICMP가 진행되지 않는다.
- DNS 장애에서는 IP 주소 통신은 가능할 수 있지만 DNS Query에 대한 정상 응답이 없어 도메인 기반 접근이 실패한다.
- HTTP 장애에서는 ARP·IP 통신·DNS까지 정상이어도 웹 서비스가 꺼져 있어 최종 웹 접속이 실패한다.

## 장애 진단 흐름

```text
ARP Reply가 오는가?
  ├─ 아니오 → Gateway, L2 구간, IP 설정 확인
  └─ 예
      └─ IP/Ping 통신이 되는가?
          ├─ 아니오 → Routing, Gateway 확인
          └─ 예
              └─ DNS Response가 오는가?
                  ├─ 아니오 → DNS 서비스 확인
                  └─ 예 → TCP/HTTP 서비스 상태 확인
```

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [전체 패킷 비교 분석](packet_analysis.md) | Gateway·DNS·HTTP 장애의 정상/장애 패킷 흐름과 관찰 포인트 |
| [office_network/](office_network/) | Packet Tracer로 구성한 VLAN 사내 네트워크와 분석 기록 |
| [네트워크 구성 명세](office_network/network_spec.md) | VLAN, IP 주소, L3/L2 스위치 구성과 통신 테스트 결과 |
| [정상 ARP·ICMP 분석](<office_network/정상 ARP+ICMP 분석.md>) | Inter-VLAN 통신에서의 게이트웨이 ARP와 ICMP 흐름 |
| [Gateway 장애 분석](office_network/gateway_장애.md) | 잘못된 게이트웨이 설정으로 ARP Reply가 사라지는 과정 |
| [Packet Tracer 분석 기록](office_network/packet_analysis_packettracer.md) | Gateway, DNS, HTTP 장애의 Packet Tracer 관찰 결과 |
| [정상 네트워크 파일](office_network/office_network.pkt) | 정상 상태 확인용 Packet Tracer 파일 |
| [Gateway 장애 파일](office_network/fault_gateway.pkt) | 잘못된 기본 게이트웨이 장애 재현용 Packet Tracer 파일 |
| [토폴로지 이미지](office_network/topology.png) | Office Network 장비·VLAN 구성 화면 |
| [정상 ARP·ICMP 캡처](office_network/normal_arp_icmp.png) | 정상 ARP와 ICMP 이벤트 관찰 화면 |
| [Wireshark 실습 가이드](wireshark/wireshark_packet_lab_scroll.html) | Wireshark 패킷 분석 실습 안내 |
| [정상 캡처](wireshark/normal.pcapng) | 정상 통신 비교용 Wireshark 캡처 |
| [Gateway 장애 캡처](wireshark/fault_gateway.pcapng) | Gateway 장애 비교용 Wireshark 캡처 |
| [DNS 장애 캡처](wireshark/fault_dns.pcapng) | DNS 장애 비교용 Wireshark 캡처 |

## 네트워크 주소 계획

| 대상 | VLAN | IP 주소 | 기본 게이트웨이 | DNS |
| --- | ---: | --- | --- | --- |
| DEV-PC1 | 10 | `192.168.10.10` | `192.168.10.1` | `192.168.10.100` |
| DEV-PC2 | 10 | `192.168.10.20` | `192.168.10.1` | `192.168.10.100` |
| DNS/Web Server | 10 | `192.168.10.100` | `192.168.10.1` | `192.168.10.100` |
| OPS-PC1 | 20 | `192.168.20.10` | `192.168.20.1` | `192.168.10.100` |
| OPS-PC2 | 20 | `192.168.20.20` | `192.168.20.1` | `192.168.10.100` |

## 실습 순서

1. [office_network.pkt](office_network/office_network.pkt)를 Cisco Packet Tracer에서 열어 VLAN, Trunk, L3 스위치 SVI 설정을 확인한다.
2. DEV-PC와 OPS-PC 사이에 Ping을 수행하고, Simulation 모드에서 ARP Request/Reply와 ICMP Echo Request/Reply를 관찰한다.
3. OPS-PC1의 기본 게이트웨이를 `192.168.20.254`로 변경한 [Gateway 장애 파일](office_network/fault_gateway.pkt)에서 ARP Reply가 사라지는 지점을 확인한다.
4. DNS 서비스를 끈 상태와 HTTP 서비스를 끈 상태를 만들어, IP Ping·도메인 이름 접속·웹 접속 결과를 비교한다.
5. Wireshark에서 `normal.pcapng`, `fault_gateway.pcapng`, `fault_dns.pcapng`를 열어 요청과 응답이 끊기는 프로토콜 단계를 비교한다.

## 준비물

- Cisco Packet Tracer (`.pkt` 파일 열기 및 Simulation 모드 사용)
- Wireshark (`.pcapng` 파일 열기 및 패킷 필터링)
