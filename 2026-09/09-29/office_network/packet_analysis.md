# 정상 상태와 장애 상태의 패킷 비교 분석

## 1. 분석 목적

이 문서는 Office Network 실습에서 **정상 상태와 장애 상태의 패킷 흐름을 비교**하여,
Packet Tracer 화면에서 **눈으로 확인할 수 있는 차이**를 정리한 자료이다.

분석 대상은 다음 3가지 장애이다.

- Gateway 장애
- DNS 장애
- HTTP/TCP 서비스 장애

핵심은 단순히 `Ping 성공/실패`만 보는 것이 아니라,
**ARP → ICMP → DNS → TCP/HTTP 중 어느 단계에서 흐름이 끊기는지 확인하는 것**이다.

---

# 2. 정상 상태 패킷

## 정상 통신 흐름

예시:

- DEV-PC1: `192.168.10.10`
- OPS-PC1: `192.168.20.10`
- VLAN 10 Gateway: `192.168.10.1`
- VLAN 20 Gateway: `192.168.20.1`
- DNS/Web Server: `192.168.10.100`

다른 VLAN으로 통신할 때 PC는 먼저 Gateway의 MAC 주소를 알아야 한다.

```text
PC
 ↓
ARP Request
 ↓
ARP Reply
 ↓
ICMP Echo Request
 ↓
Router / L3 Switch
 ↓
목적지
 ↓
ICMP Echo Reply
```

### 정상 상태에서 눈에 보이는 특징

| 확인 항목 | 정상 상태에서 보이는 모습 |
|---|---|
| ARP Request | 발생함 |
| ARP Reply | Request 뒤에 정상적으로 발생함 |
| Gateway 주소 | 정상 Gateway를 대상으로 요청 |
| ICMP Echo Request | 목적지까지 전달됨 |
| ICMP Echo Reply | 출발지까지 다시 돌아옴 |
| DNS Query | DNS Server로 전달됨 |
| DNS Response | Query에 대한 응답이 돌아옴 |
| 웹 접속 | DNS 해석 후 서비스 연결까지 진행됨 |

즉 정상 상태에서는 대부분의 요청이 다음과 같이 **Request와 Reply가 한 쌍으로 보인다.**

```text
ARP Request  → ARP Reply
ICMP Request → ICMP Reply
DNS Query    → DNS Response
```

---

# 3. Gateway 장애 패킷 비교

## 장애 설정

OPS-PC1의 Gateway를 정상 주소가 아닌 존재하지 않는 주소로 변경하였다.

```text
정상 Gateway : 192.168.20.1
장애 Gateway : 192.168.20.254
```

OPS-PC1이 다른 네트워크로 패킷을 보내려면 먼저 Gateway의 MAC 주소가 필요하다.
따라서 `192.168.20.254`를 대상으로 ARP Request를 전송한다.

하지만 해당 IP를 사용하는 Gateway가 존재하지 않기 때문에 ARP Reply가 돌아오지 않는다.

## 정상 / Gateway 장애 비교

| 항목 | 정상 | Gateway 장애 | 눈에 보이는 차이 |
|---|---|---|---|
| ARP Request | 있음 | 있음 | 둘 다 ARP 요청은 발생 |
| ARP Target IP | `192.168.20.1` | `192.168.20.254` | **요청 대상 IP가 다름** |
| ARP Reply | 있음 | 없음 | **장애에서는 Reply가 보이지 않음** |
| ICMP Request | 목적지까지 전달 | 진행되지 않음 | **ARP 이후 ICMP 흐름이 끊김** |
| ICMP Reply | 있음 | 없음 | 응답 패킷 없음 |
| Ping 결과 | 성공 | 실패 | 최종 통신 실패 |

### 화면에서 가장 먼저 볼 부분

정상 상태:

```text
ARP Request
    ↓
ARP Reply
    ↓
ICMP Echo Request
    ↓
ICMP Echo Reply
```

Gateway 장애:

```text
ARP Request
    ↓
응답 없음
    ↓
ICMP 전달 불가
```

### 핵심 관찰 포인트

> **ARP Request는 보이는데 ARP Reply가 없다.**

이 패턴이 보이면 먼저 Gateway IP 또는 같은 LAN 구간의 주소 설정을 확인할 수 있다.

---

# 4. DNS 장애 패킷 비교

## 장애 설정

DNS Server의 DNS 서비스를 중지한다.

```text
Server → Services → DNS → Off
```

이 상태에서는 서버 자체의 IP 통신은 가능할 수 있지만,
도메인 이름을 IP 주소로 변환하는 과정이 정상적으로 완료되지 않는다.

## 정상 / DNS 장애 비교

| 항목 | 정상 | DNS 장애 | 눈에 보이는 차이 |
|---|---|---|---|
| ARP | 정상 | 정상 가능 | 네트워크 자체는 살아 있음 |
| IP Ping | 성공 | 성공 가능 | IP 직접 통신은 가능할 수 있음 |
| DNS Query | 있음 | 있음 | 요청 자체는 서버까지 갈 수 있음 |
| DNS Response | 있음 | 없거나 실패 | **DNS 응답이 정상적으로 돌아오지 않음** |
| 이름 → IP 변환 | 성공 | 실패 | 도메인 이름 해석 실패 |
| 도메인 웹 접속 | 성공 | 실패 | 이름 기반 접속 실패 |

### 정상 상태

```text
PC
 ↓
DNS Query
 ↓
DNS Server
 ↓
DNS Response
 ↓
IP 주소 확인
 ↓
웹 서버 접속
```

### DNS 장애 상태

```text
PC
 ↓
DNS Query
 ↓
DNS Server
 ↓
DNS Response 없음 / 실패
 ↓
이름 해석 실패
```

### 눈에 보이는 핵심 차이

정상:

```text
DNS Query → DNS Response
```

장애:

```text
DNS Query → 응답 없음 또는 실패
```

그리고 다음과 같은 차이가 나타날 수 있다.

```text
ping 192.168.10.100
→ 성공 가능

www.company.local
→ 접속 실패
```

### 핵심 관찰 포인트

> **IP로는 통신되는데 이름으로는 접속되지 않는다.**

이 경우 네트워크 전체 장애보다는 DNS 단계부터 확인하는 것이 좋다.

---

# 5. HTTP/TCP 서비스 장애 패킷 비교

## 장애 설정

DNS는 정상적으로 유지하고 Web Server의 HTTP 서비스만 중지한다.

```text
Server → Services → HTTP → Off
```

즉,

- Gateway 정상
- IP 통신 정상
- DNS 정상
- Web 서비스만 장애

인 상태이다.

## 정상 / HTTP 장애 비교

| 항목 | 정상 | HTTP/TCP 장애 | 눈에 보이는 차이 |
|---|---|---|---|
| ARP | 정상 | 정상 | 주소 확인 단계 정상 |
| ICMP Ping | 성공 | 성공 가능 | 서버 자체에는 도달 가능 |
| DNS Query | 있음 | 있음 | DNS 요청 정상 |
| DNS Response | 있음 | 있음 | 이름 해석 정상 |
| 웹 서비스 접속 | 성공 | 실패 | **최종 서비스 단계에서만 실패** |
| 브라우저 결과 | 페이지 표시 | 페이지 표시 안 됨 | 네트워크는 살아 있지만 서비스 사용 불가 |

### 정상 상태

```text
ARP 정상
 ↓
IP 통신 정상
 ↓
DNS Query / Response 정상
 ↓
Web Service 연결
 ↓
페이지 표시
```

### HTTP 장애 상태

```text
ARP 정상
 ↓
IP 통신 정상
 ↓
DNS Query / Response 정상
 ↓
Web Service 연결 단계
 ↓
실패
```

### 핵심 관찰 포인트

> **DNS까지는 정상인데 웹페이지가 열리지 않는다.**

따라서 이 경우에는 Gateway나 DNS보다 **TCP/HTTP 서비스 상태**를 우선 확인할 수 있다.

---

# 6. 세 장애의 패킷 차이 한눈에 보기

| 구분 | ARP | ICMP / IP 통신 | DNS | HTTP | 패킷에서 보이는 핵심 특징 |
|---|---|---|---|---|---|
| 정상 | 정상 | 정상 | 정상 | 정상 | Request 뒤에 Reply가 정상적으로 이어짐 |
| Gateway 장애 | **실패** | 실패 | 영향 | 영향 | **ARP Request만 있고 Reply가 없음** |
| DNS 장애 | 정상 | 정상 가능 | **실패** | 이름 기반 접근 실패 | **DNS Query 뒤 정상 Response가 없음** |
| HTTP 장애 | 정상 | 정상 | 정상 | **실패** | DNS까지 정상인데 최종 웹 서비스 단계에서 실패 |

---

# 7. 패킷만 보고 장애 위치 좁히기

패킷을 다음 순서로 확인하면 장애 위치를 빠르게 좁힐 수 있다.

```text
1. ARP Reply가 오는가?
       │
       ├─ NO → Gateway / L2 구간 / IP 설정 확인
       │
       └─ YES
            ↓
2. IP 또는 Ping 통신이 되는가?
       │
       ├─ NO → Routing / Gateway 확인
       │
       └─ YES
            ↓
3. DNS Response가 오는가?
       │
       ├─ NO → DNS 서비스 확인
       │
       └─ YES
            ↓
4. 웹 서비스가 연결되는가?
       │
       ├─ NO → TCP / HTTP 서비스 확인
       │
       └─ YES → 정상
```

---

# 8. 핵심 문장

정상 상태에서는 **요청 패킷 다음에 응답 패킷이 정상적으로 이어집니다.**

반면 장애 상태에서는 특정 단계부터 응답이 사라지기 때문에,
**어느 프로토콜까지 정상적으로 동작했는지를 확인하면 장애 위치를 좁힐 수 있습니다.**

예를 들어 Gateway 장애에서는 ARP Request는 발생하지만 ARP Reply가 없고,
그 결과 ICMP 패킷이 다른 VLAN으로 진행되지 못합니다.

DNS 장애에서는 IP 통신은 가능하지만 DNS Query에 대한 정상적인 응답이 없어
도메인 이름을 이용한 접속이 실패합니다.

HTTP 장애에서는 ARP, IP 통신, DNS까지 모두 정상적으로 동작하지만
최종 웹 서비스 연결 단계에서 실패합니다.

---

# 9. 최종 정리

패킷 분석에서 중요한 것은 단순히 **"통신이 된다 / 안 된다"**를 확인하는 것이 아니다.

정상 패킷과 장애 패킷을 비교하면서

```text
어디까지 정상인가?
        ↓
어디서부터 응답이 사라지는가?
```

를 확인하는 것이 핵심이다.

이번 실습에서는 다음과 같이 구분할 수 있었다.

- **ARP Reply가 없다 → Gateway 계층 문제 의심**
- **IP 통신은 되지만 DNS Response가 없다 → DNS 문제 의심**
- **DNS까지 정상인데 웹 접속이 안 된다 → HTTP/TCP 서비스 문제 의심**

따라서 패킷을 **ARP → ICMP → DNS → TCP/HTTP 순서로 확인하면 장애 범위를 단계적으로 좁힐 수 있다.**
