# Packet Analysis

## 분석 목적

Packet Tracer에서 구성한 VLAN 네트워크를 기준으로 정상 상태와 장애 상태의 패킷 흐름을 비교하였다.

분석한 장애는 다음 3가지이다.

1. Gateway 장애
2. DNS 장애
3. TCP/HTTP 장애

---

# 1. Gateway 장애

## 정상 상태

DEV-PC1(`192.168.10.10`)과 OPS-PC1(`192.168.20.10`) 간 통신을 테스트하였다.

정상 Gateway:

- VLAN 10: `192.168.10.1`
- VLAN 20: `192.168.20.1`

다른 VLAN으로 패킷을 보내기 위해 PC는 먼저 Gateway의 MAC 주소를 확인한다.

```text
OPS-PC1
   ↓
ARP Request
"192.168.20.1의 MAC 주소는?"
   ↓
L3 Switch
   ↓
ARP Reply
   ↓
Gateway MAC 주소 학습
   ↓
ICMP Echo Request
   ↓
Inter-VLAN Routing
   ↓
ICMP Echo Reply
```

정상 상태에서는 ARP를 통해 Gateway의 MAC 주소를 확인한 후 ICMP Echo Request/Reply가 정상적으로 전달된다.

## 장애 상태

OPS-PC1의 Gateway를 의도적으로 변경하였다.

정상:

```text
192.168.20.1
```

장애:

```text
192.168.20.254
```

OPS-PC1은 다른 네트워크로 패킷을 보내기 위해 `192.168.20.254`의 MAC 주소를 ARP로 요청한다.

```text
OPS-PC1
   ↓
ARP Request
"192.168.20.254 누구야?"
   ↓
ARP Reply 없음
   ↓
Gateway MAC 주소 확인 실패
   ↓
ICMP 전달 실패
```

해당 IP를 사용하는 Gateway가 존재하지 않기 때문에 ARP Reply를 받지 못하고 다른 VLAN으로 ICMP 패킷을 전달할 수 없다.

## 정상 / 장애 비교

| 항목 | 정상 | Gateway 장애 |
|---|---|---|
| ARP Request | 발생 | 발생 |
| ARP Target | `192.168.20.1` | `192.168.20.254` |
| ARP Reply | 있음 | 없음 |
| Gateway MAC 학습 | 성공 | 실패 |
| ICMP Request 전달 | 성공 | 실패 |
| ICMP Reply | 있음 | 없음 |
| 최종 결과 | Ping 성공 | Ping 실패 |

### 핵심 분석

**Gateway 장애에서는 다른 VLAN으로 패킷을 전달하기 전에 Gateway의 MAC 주소를 찾는 ARP 단계부터 문제가 발생한다.**

---

# 2. DNS 장애

## 정상 상태

DNS/Web Server:

```text
192.168.10.100
```

DEV-PC2가 `www.company.local`에 접속한다고 가정한다.

DNS Server의 MAC 주소가 ARP Cache에 없다면 먼저 ARP가 수행된다.

```text
DEV-PC2
   │
   │ DNS Server의 MAC 주소를 모름
   ▼
ARP Request
   │
   ▼
L2 SW-A ─── Broadcast
   ├── DEV-PC1
   ├── Server (192.168.10.100)
   └── L3 Switch
          ↓
Server가 ARP Reply
          ↓
DEV-PC2가 Server MAC 학습
          ↓
DNS Query
          ↓
DNS Server
          ↓
DNS Response
```

ARP로 알아낸 IP와 MAC 주소의 관계는 ARP Cache에 일정 시간 저장된다.

확인 명령:

```text
arp -a
```

즉,

> **ARP는 MAC 주소를 알아내는 과정이고, ARP Cache는 알아낸 IP ↔ MAC 관계를 잠시 기억하는 곳이다.**

정상 DNS 통신에서는 다음 흐름이 나타난다.

```text
DNS Query
   ↓
DNS Response
   ↓
www.company.local
   ↓
192.168.10.100
```

## 장애 상태

Server에서 DNS 서비스를 중지하였다.

```text
Server
→ Services
→ DNS
→ Off
```

DNS 장애가 발생해도 Server의 네트워크 연결 자체가 끊어진 것은 아니다.

따라서 다음과 같은 차이가 발생할 수 있다.

```text
ping 192.168.10.100
→ 성공

www.company.local
→ 실패
```

## 정상 / 장애 비교

| 확인 | 정상 | DNS 장애 |
|---|---|---|
| ARP | 정상 | 정상 가능 |
| DNS Query | 있음 | 있음 |
| DNS Response | 있음 | 없거나 실패 |
| 이름 → IP 변환 | 성공 | 실패 |
| `192.168.10.100` Ping | 성공 | 성공 가능 |
| 도메인 웹 접속 | 성공 | 실패 |

### 핵심 분석

**IP 주소로는 통신이 되는데 도메인 이름으로 접속되지 않는다면 DNS 장애를 우선 의심할 수 있다.**

---

# 3. TCP/HTTP 장애

## 정상 상태

Server에서 DNS와 HTTP 서비스를 모두 정상적으로 실행한다.

```text
DNS  : ON
HTTP : ON
```

정상적인 웹 접속 흐름은 다음과 같다.

```text
도메인 입력
   ↓
DNS Query / Response
   ↓
Server IP 확인
   ↓
웹 서비스 연결
   ↓
웹페이지 표시
```

일반적인 TCP 연결에서는 3-Way Handshake가 사용된다.

```text
Client                  Server
  │                        │
  │ ------- SYN ---------> │
  │ <---- SYN / ACK ------ │
  │ ------- ACK ---------> │
  │                        │
  │     연결 성립           │
```

## 장애 상태

Server의 HTTP 서비스만 중지하였다.

```text
DNS  : ON
HTTP : OFF
```

즉 Server 자체와 DNS는 살아 있지만 웹 서비스만 사용할 수 없는 상태이다.

```text
DNS Query
   ↓
DNS Response
   ↓
Server IP 확인
   ↓
웹 서비스 접근
   ↓
HTTP Service OFF
   ↓
웹페이지 표시 실패
```

Packet Tracer Simulation에서 TCP 이벤트가 명확하게 나타나지 않은 경우에는 RST 또는 Retransmission이 발생했다고 임의로 판단하지 않고 실제 관찰 결과만 기록한다.

## 정상 / 장애 비교

| 확인 | 정상 | HTTP/TCP 장애 |
|---|---|---|
| Server Ping | 성공 | 성공 |
| DNS | 정상 | 정상 |
| 이름 → IP 변환 | 성공 | 성공 |
| HTTP Service | ON | OFF |
| 웹페이지 | 표시됨 | 표시되지 않음 |
| 최종 결과 | 웹 접속 성공 | 웹 접속 실패 |

### 핵심 분석

**Ping과 DNS가 모두 정상인데 웹페이지에 접속할 수 없다면 네트워크 경로나 DNS보다 Server의 HTTP 서비스 상태를 확인해야 한다.**

---

# 4. 세 가지 장애 종합 비교

| 장애 | Ping | DNS | TCP/HTTP | 핵심 증상 |
|---|---|---|---|---|
| 정상 | ✅ | ✅ | ✅ | 모두 정상 |
| Gateway 오류 | ❌ 다른 VLAN 통신 실패 | 영향 가능 | 영향 가능 | Gateway ARP 단계부터 문제 |
| DNS OFF | ✅ | ❌ | IP 직접 접근은 가능할 수 있음 | 도메인 이름 해석 실패 |
| HTTP OFF | ✅ | ✅ | ❌ | Server까지 통신되지만 웹 접속 실패 |

---

# 5. 최종 분석

세 장애는 사용자 입장에서는 모두 "접속이 안 된다"는 현상으로 보일 수 있지만 패킷 흐름을 확인하면 장애 위치가 다르다.

```text
Gateway 장애
→ ARP / 다른 VLAN 전달 단계 확인

DNS 장애
→ IP 통신은 정상
→ 이름 해석 단계 실패

HTTP/TCP 장애
→ IP 통신 정상
→ DNS 정상
→ 최종 웹 서비스 접속 실패
```

따라서 장애 분석 시 다음 순서로 확인하면 문제 범위를 좁히기 쉽다.

```text
ARP
 ↓
ICMP (Ping)
 ↓
DNS
 ↓
TCP / HTTP
```

이번 실습을 통해 정상 상태와 장애 상태를 비교하면 **Gateway 장애, DNS 장애, Web Service 장애가 패킷 흐름에서 서로 다른 형태로 나타난다는 점**을 확인할 수 있었다.
