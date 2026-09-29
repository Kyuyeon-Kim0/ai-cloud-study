# 2026-09-23 (수) 학습 기록

## 학습 주제

- IPv4·IPv6, CIDR, ping, traceroute를 통한 IP 네트워크 기초
- OSI 1~3계층: 물리 계층, 데이터링크 계층, 네트워크 계층
- Linux에서 프로세스·포트·트래픽·패킷을 확인하는 방법
- Scapy로 패킷을 생성·저장·변형하고 Wireshark로 분석하는 방법
- GPT API와 Multipass VM을 연결한 네트워크·패킷 진단 에이전트

## 핵심 이해

### 계층별 진단 순서

- 통신 문제는 하위 계층부터 확인한다. 물리 링크(L1), MAC·ARP(L2), IP·라우팅·ICMP(L3) 순서로 범위를 좁힌다.
- IP 주소는 종단 간 통신을 위한 논리 주소이고, MAC 주소는 같은 링크 구간에서 프레임을 전달하기 위한 주소이다.
- `ping`은 IP 연결을, `traceroute`는 목적지까지의 경로를, `ss`는 포트의 LISTEN 상태를 확인하는 데 사용한다.

### 패킷 관찰과 분석

- `htop`, `ss`, `iftop`, `tcpdump`를 사용하면 프로세스부터 실제 패킷까지 단계적으로 원인을 추적할 수 있다.
- pcap 파일에는 캡처한 패킷을 저장할 수 있고, Wireshark 또는 `tcpdump -r`로 다시 분석할 수 있다.
- TCP 3-way handshake에서는 SYN → SYN/ACK → ACK 흐름과 포트, Sequence/Ack 번호, 플래그를 함께 읽는다.
- Payload를 바꾼 패킷은 길이와 체크섬을 다시 계산해야 정상적인 패킷 구조를 유지한다.

### AI 진단 에이전트

- OpenAI Agents SDK의 도구 함수로 `ping`, 포트 LISTEN 확인, HTTP 프로세스 확인, HTTP 요청, pcap 분석을 에이전트에 제공할 수 있다.
- 에이전트는 실제 도구 실행 결과를 근거로 상태를 판단해야 하며, 확인하지 않은 사실을 추정해 답하지 않도록 설계한다.

## 학습 자료

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [IPv4·IPv6와 네트워크 보안](<3_네트워크/1. ipv4_network_교안.html>) | 네트워크 기초, IPv4/IPv6, 서브넷과 보안 |
| [물리 계층(L1)](<3_네트워크/2. network_L1_물리계층_교안.html>) | 신호, 링크, 대역폭, 감쇠, 자동 협상 |
| [데이터링크 계층(L2)](<3_네트워크/3. network_L2_데이터링크계층_교안.html>) | Ethernet, MAC, ARP, 스위치 |
| [네트워크 계층(L3)](<3_네트워크/4. network_L3_네트워크계층_교안.html>) | IP 패킷, 라우팅, TTL, MTU, ICMP |
| [Wireshark 초보자 가이드](3_네트워크/wireshark-beginner-guide.html) | 캡처와 기본 필터, 패킷 구조 읽기 |
| [IPv4·CIDR·ping·traceroute 퀴즈](3_네트워크/퀴즈_1번_ipv4_ping_traceroute_cidr_practical_quiz.html) | 실습형 이해도 점검 |
| [프로세스·포트·트래픽·패킷 분석](<3_네트워크/프로세스·포트·트래픽·패킷 분석 실습.html>) | Multipass 3VM에서 `htop`·`ss`·`iftop`·`tcpdump` 실습 |
| [리눅스 패킷 생성·분석·변형 실습](<3_네트워크/리눅스패킷 생성.분석,변형실습/>) | Scapy, pcap, Ethernet, TCP, 체크섬, GPT 에이전트 실습 자료 |
| [GPT API 기반 네트워크 진단 에이전트](<3_네트워크/에이전트_네트워크진단도구/에이전트_GPT API 기반 리눅스 네트워크 진단 에이전트 만들기.html>) | Multipass 환경에서 진단 도구를 사용하는 에이전트 만들기 |

## 패킷 실습 순서

1. [Step 1](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step1_scapy_udp_payload.html>) — Scapy로 UDP 패킷을 만들고 Payload 변경하기
2. [Step 2](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step2_pcap_wireshark_reviewed.html>) — pcap 저장 및 Wireshark 비교 분석
3. [Step 3](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step3_ethernet_mac_detailed.html>) — Ethernet 프레임과 MAC 주소 직접 구성
4. [Step 4](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step4_tcp_handshake_detailed.html>) — TCP 3-way handshake 분석
5. [Step 5](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step5_pcap_modify_checksum_detailed.html>) — pcap Payload 수정과 Length·Checksum 재계산
6. [Step 6](<3_네트워크/리눅스패킷 생성.분석,변형실습/packet_lab_step6_gpt_agent.html>) — GPT API 네트워크·패킷 분석 에이전트

## 에이전트 실행

에이전트는 Windows 호스트에서 `multipass exec`로 `ubuntu`와 `ubuntu1` VM을 점검한다. 먼저 두 VM과 TCP 8000 포트의 테스트 HTTP 서버를 준비하고, OpenAI API 키를 환경 변수로 설정한다.

```powershell
cd C:\ai-starter\2026-09\09-23\3_네트워크\에이전트_네트워크진단도구
python gpt_network_agent.py
```

패킷 분석 기능까지 포함한 확장 에이전트는 다음 파일이다.

```powershell
python "C:\ai-starter\2026-09\09-23\3_네트워크\리눅스패킷 생성.분석,변형실습\linux_packet_lab_part6_agent.py"
```

실행 전에는 프로젝트 안내에 맞는 OpenAI Agents SDK와 필요한 네트워크 도구를 설치하고, API 키는 코드에 넣지 말고 환경 변수 또는 `.env`로 관리한다.
