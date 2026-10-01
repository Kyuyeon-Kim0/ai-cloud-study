# k3s Kubernetes API Timeout 장애 대응 사례

## 1. 개요

Multipass Ubuntu VM에 k3s를 설치한 뒤 Kubernetes 노드 상태를 확인하는
과정에서 `kubectl get nodes` 명령이 정상적으로 응답하지 않는 문제가
발생했다.

단순히 k3s를 재설치하지 않고 **서비스 상태 → API 포트 → 로그 → 시스템
자원** 순서로 점검하여 원인을 확인하고 해결했다.

------------------------------------------------------------------------

## 2. 문제 상황

다음 명령으로 노드 상태를 확인했다.

``` bash
sudo k3s kubectl get nodes
```

하지만 정상적인 노드 정보 대신 다음 오류가 발생했다.

``` text
couldn't get current server API group list:
Get "https://127.0.0.1:6443/api?timeout=32s":
context deadline exceeded
```

즉, `kubectl`이 Kubernetes API Server의 응답을 기다리다가 타임아웃된
상태였다.

------------------------------------------------------------------------

## 3. 1차 점검 - k3s 서비스 확인

먼저 k3s 서비스가 실행 중인지 확인했다.

``` bash
sudo systemctl status k3s --no-pager | head -5
```

확인 결과:

``` text
● k3s.service - Lightweight Kubernetes
Loaded: loaded
Active: active (running)
```

### 판단

k3s 서비스 자체는 실행 중이었다.

따라서 단순히 `k3s 서비스가 꺼져 있어서 발생한 문제`는 아니라고
판단했다.

------------------------------------------------------------------------

## 4. 2차 점검 - Kubernetes API 포트 확인

k3s의 Kubernetes API Server가 사용하는 `6443` 포트를 확인했다.

``` bash
sudo ss -lntp | grep 6443
```

확인 결과:

``` text
LISTEN 0 4096 *:6443 *:* users:(("k3s-server",pid=7619,fd=12))
```

### 판단

API Server 프로세스가 실제로 `6443` 포트를 열고 있었다.

즉,

``` text
k3s 서비스 실행
        ↓
API Server 6443 LISTEN
        ↓
그런데 kubectl 요청은 Timeout
```

상태였다.

------------------------------------------------------------------------

## 5. 3차 점검 - k3s 로그 확인

다음 명령으로 k3s 로그를 확인했다.

``` bash
sudo journalctl -u k3s -n 50 --no-pager
```

로그에서는 다음과 같은 메시지가 반복되었다.

``` text
Slow SQL
http: Handler timeout
context deadline exceeded
Failed to update lease
```

일부 SQL 작업은 약 6\~10초 이상 소요되고 있었다.

### 판단

API Server 자체가 실행되지 않는 것이 아니라, k3s 내부 데이터 처리 속도가
매우 느려져 요청을 제한 시간 안에 처리하지 못하고 있는 것으로 판단했다.

흐름을 단순화하면 다음과 같다.

``` text
kubectl
   ↓
Kubernetes API Server
   ↓
Kine / SQLite
   ↓
처리 지연
   ↓
API Server 응답 지연
   ↓
context deadline exceeded
```

------------------------------------------------------------------------

## 6. 4차 점검 - VM 시스템 자원 확인

시스템 자원 부족 가능성을 확인하기 위해 다음 명령을 실행했다.

``` bash
free -h
df -h
nproc
uptime
```

### 메모리

``` text
Mem:  1.9Gi total
      1.8Gi used
       71Mi free
       16Mi available

Swap: 0B
```

사용 가능한 메모리가 약 **16MiB**밖에 남아 있지 않았고 Swap도 설정되어
있지 않았다.

### CPU

``` text
nproc
2
```

CPU는 2 Core였다.

### Load Average

``` text
load average: 9.80, 9.18, 4.40
```

2 Core 환경에서 Load Average가 약 `9.80`까지 올라간 상태였다.

### 디스크

``` text
/dev/sda1
Size: 8.7G
Used: 6.9G
Avail: 1.8G
Use%: 80%
```

디스크 역시 여유 공간이 많지 않았다.

------------------------------------------------------------------------

## 7. 원인

점검 결과 핵심 원인은 **Multipass VM의 부족한 시스템 자원**이었다.

당시 VM 환경:

  항목                             상태
  --------------- ---------------------
  RAM                            약 2GB
  사용 RAM                     약 1.8GB
  Available RAM                 약 16MB
  Swap                               0B
  CPU                            2 Core
  Load Average                     9.80
  Disk              약 8.7GB / 80% 사용

메모리가 거의 고갈된 상태에서 k3s의 여러 Kubernetes 구성요소가 동시에
실행되면서 내부 데이터 처리 속도가 크게 저하되었다.

결과적으로 다음과 같은 장애 흐름이 발생했다.

``` text
Multipass VM 자원 부족
        ↓
k3s 내부 처리 지연
        ↓
Kine / SQLite Slow SQL
        ↓
Kubernetes API Server 응답 지연
        ↓
Handler Timeout
        ↓
kubectl context deadline exceeded
```

------------------------------------------------------------------------

## 8. 해결 방법

Multipass VM의 자원을 증설했다.

Windows PowerShell에서 VM을 중지한 뒤 CPU, RAM, 디스크 자원을 늘렸다.

예:

``` powershell
multipass stop myUbuntu

multipass set local.myUbuntu.memory=4G
multipass set local.myUbuntu.cpus=4
multipass set local.myUbuntu.disk=20G

multipass start myUbuntu
```

VM에 다시 접속한 뒤 k3s를 확인했다.

``` bash
sudo systemctl restart k3s
```

------------------------------------------------------------------------

## 9. 해결 결과

다시 Kubernetes 노드를 조회했다.

``` bash
sudo k3s kubectl get nodes
```

최종 결과:

``` text
NAME       STATUS   ROLES           AGE   VERSION
myubuntu   Ready    control-plane   11m   v1.36.4+k3s1
```

`STATUS`가 **Ready**로 표시되면서 Kubernetes 노드가 정상 상태로 복구된
것을 확인했다.

------------------------------------------------------------------------

## 10. 장애 대응 과정 요약

``` text
[장애 발생]
kubectl get nodes
→ context deadline exceeded

        ↓

[서비스 확인]
systemctl status k3s
→ active (running)

        ↓

[포트 확인]
ss -lntp | grep 6443
→ API Server 6443 LISTEN

        ↓

[로그 확인]
journalctl -u k3s
→ Slow SQL
→ Handler timeout
→ context deadline exceeded

        ↓

[시스템 자원 확인]
RAM available ≈ 16MB
CPU = 2 Core
Load Average = 9.80
Swap = 0

        ↓

[원인 판단]
Multipass VM 자원 부족

        ↓

[조치]
CPU / RAM / Disk 증설

        ↓

[검증]
kubectl get nodes
→ Ready

        ↓

[복구 완료]
```

------------------------------------------------------------------------

## 11. 배운 점

이번 장애를 통해 프로세스가 실행 중이라는 사실만으로 서비스 전체가
정상이라고 판단하면 안 된다는 점을 확인했다.

특히 Kubernetes와 같은 시스템에서는 다음 순서로 장애를 확인하는 것이
효과적이었다.

1.  **서비스 상태 확인**
    -   `systemctl status`
2.  **네트워크 및 포트 확인**
    -   `ss -lntp`
3.  **애플리케이션 로그 확인**
    -   `journalctl`
4.  **CPU / RAM / Disk 등 시스템 자원 확인**
    -   `free`
    -   `df`
    -   `nproc`
    -   `uptime`
5.  **조치 후 실제 서비스 상태 검증**
    -   `kubectl get nodes`

이번 사례에서는 k3s를 삭제하거나 재설치하지 않고 단계적으로 원인을 좁혀
**VM 자원 부족이 Kubernetes API Timeout으로 이어지고 있음을 확인하고
해결했다.**

------------------------------------------------------------------------

## 12. 핵심 한 줄

> **서비스가 실행 중이어도 시스템 자원이 부족하면 내부 처리 지연으로 API
> Timeout이 발생할 수 있으므로, 장애 대응 시 서비스·포트·로그뿐 아니라
> CPU와 메모리 같은 시스템 자원도 함께 확인해야 한다.**
