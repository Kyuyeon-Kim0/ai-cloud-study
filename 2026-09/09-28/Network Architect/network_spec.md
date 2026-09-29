# PacketLab Network Specification

## 1. 네트워크 개요

PacketLab 사내 네트워크의 개발팀, 운영팀, 서버망을 VLAN으로 분리하여 구성하였다.

Cisco 2960 스위치를 이용하여 VLAN을 구성하고, Cisco 2911 라우터에서 Router-on-a-Stick 방식으로 VLAN 간 라우팅을 수행한다.

## 2. Topology

```text
                    R1
                  [2911]
                     |
               802.1Q Trunk
                     |
                    SW1
                  [2960]
              /      |      \
          DEV-PC   OPS-PC   SERVER
          VLAN10   VLAN20   VLAN30
```

## 3. IPv4 / VLAN 설계

| 구분 | VLAN | IP Address | Gateway |
|---|---:|---|---|
| DEV-PC | 10 | 192.168.10.10/24 | 192.168.10.1 |
| OPS-PC | 20 | 192.168.20.10/24 | 192.168.20.1 |
| SERVER | 30 | 192.168.30.10/24 | 192.168.30.1 |

## 4. Switch 구성

| Switch Port | 연결 장비 | 설정 |
|---|---|---|
| Fa0/1 | DEV-PC | Access VLAN 10 |
| Fa0/2 | OPS-PC | Access VLAN 20 |
| Fa0/3 | SERVER | Access VLAN 30 |
| Gi0/1 | R1 | Trunk VLAN 10,20,30 |

## 5. Gateway 구성

R1의 Gi0/0 인터페이스에 VLAN별 Subinterface를 구성하였다.

| Interface | VLAN | Gateway |
|---|---:|---|
| Gi0/0.10 | 10 | 192.168.10.1/24 |
| Gi0/0.20 | 20 | 192.168.20.1/24 |
| Gi0/0.30 | 30 | 192.168.30.1/24 |

## 6. Routing 방식

Router-on-a-Stick 방식을 사용하였다.

SW1과 R1 사이를 802.1Q Trunk로 구성하여 VLAN 10, 20, 30의 트래픽을 하나의 물리 링크를 통해 전달한다.

R1에서 VLAN 간 Layer 3 Routing을 수행한다.

## 7. 정상 통신 확인

DEV-PC에서 SERVER로 ICMP 테스트를 수행하였다.

```text
DEV-PC 192.168.10.10
        ↓
      VLAN 10
        ↓
       SW1
        ↓
       R1
        ↓
      VLAN 30
        ↓
SERVER 192.168.30.10
```

테스트 명령:

```text
ping 192.168.30.10
```

결과:

```text
Sent = 4
Received = 4
Lost = 0 (0% loss)
```

따라서 VLAN 10과 VLAN 30 사이의 라우팅 및 기본 네트워크 통신이 정상적으로 동작함을 확인하였다.

## 8. 정상 기준 환경

본 네트워크를 이후 장애 분석을 위한 정상 기준 환경(Baseline)으로 사용한다.

정상 상태의 패킷과 VLAN, DNS, Routing 등의 장애 상태에서 발생하는 패킷을 비교하여 장애 원인을 분석한다.