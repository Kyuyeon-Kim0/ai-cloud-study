# Multipass SSH Timeout 장애 대응 기록

## 1. 장애 개요

Multipass 인스턴스 `myUbuntu`는 `multipass list`에서 `Running` 상태로 표시되었지만,
실제 SSH 접속과 Multipass shell 접속이 모두 정상적으로 동작하지 않았다.

발생 증상:

```text
ssh myUbuntu
```

실행 시 연결이 오래 걸리거나 응답이 없었음.

또한:

```powershell
multipass shell myUbuntu
```

실행 시 다음 오류 발생:

```text
shell failed: ssh connection failed: 'Timeout connecting to myUbuntu.mshome.net'
```

---

## 2. 장애 판단

처음에는 VS Code Remote-SSH 문제처럼 보였으나,
`multipass shell myUbuntu`도 SSH timeout이 발생했기 때문에
문제 범위가 VS Code가 아니라 Multipass VM 또는 VM 네트워크 쪽으로 좁혀졌다.

즉 다음과 같이 판단할 수 있다.

```text
VS Code 문제 가능성 낮음
        ↓
Windows SSH도 지연
        ↓
multipass shell도 timeout
        ↓
Multipass VM 내부 SSH 응답 또는 VM 네트워크 문제 가능성 높음
```

`multipass list`에서 `Running` 상태라고 표시되더라도
실제로 SSH 서비스가 정상 응답 중이라는 의미는 아니다.

---

## 3. 점검 절차

### 3-1. Multipass 인스턴스 상태 확인

```powershell
multipass list
```

예시:

```text
Name       State    IPv4           Image
myUbuntu   Running  172.18.21.139  Ubuntu 24.04 LTS
```

`Running` 상태인지 확인한다.

---

### 3-2. SSH 상세 로그 확인

```powershell
ssh -vvv myUbuntu
```

다음과 같이 TCP 연결까지 성공할 수 있다.

```text
Connecting to 172.18.21.139 [172.18.21.139] port 22.
Connection established.
Local version string SSH-2.0-OpenSSH_for_Windows_9.5
```

여기서 이후 로그가 진행되지 않는다면,
Windows에서 VM의 22번 포트까지는 연결되지만
VM 내부 SSH 서버가 정상적으로 응답하지 않는 상태일 가능성이 있다.

---

### 3-3. Multipass shell 확인

```powershell
multipass shell myUbuntu
```

다음과 같이 timeout이 발생했다.

```text
shell failed: ssh connection failed: 'Timeout connecting to myUbuntu.mshome.net'
```

이 결과를 통해 VS Code Remote-SSH 문제가 아니라
Multipass VM 자체 또는 VM 네트워크 문제로 판단하였다.

---

## 4. 복구 절차

### 4-1. 일반 종료 시도

```powershell
multipass stop myUbuntu
```

하지만 VM이 비정상 상태일 경우 종료 명령도 장시간 응답하지 않을 수 있다.

이 경우 실행 중인 명령은 `Ctrl + C`로 중단한다.

---

### 4-2. 강제 종료

관리자 권한 PowerShell에서 다음 명령을 실행한다.

```powershell
multipass stop --force myUbuntu
```

강제 종료 후 상태 확인:

```powershell
multipass list
```

정상적으로 종료되었다면:

```text
myUbuntu   Stopped
```

처럼 표시된다.

> 주의: `--force`는 VM을 강제로 종료하기 때문에
> VM 내부에서 파일 쓰기 작업이 진행 중이었다면 데이터 손상 가능성이 있다.
> 일반 종료가 불가능할 때 사용한다.

---

### 4-3. VM 다시 시작

```powershell
multipass start myUbuntu
```

이후 다시 상태를 확인한다.

```powershell
multipass list
```

예시:

```text
Name       State    IPv4          Image
myUbuntu   Running  172.18.27.40  Ubuntu 24.04 LTS
```

VM 재시작 후 IPv4 주소가 변경될 수 있다.

기존:

```text
172.18.21.139
```

재시작 후:

```text
172.18.27.40
```

---

## 5. SSH 설정 갱신

Multipass VM IP가 변경된 경우 Windows의 SSH config도 수정해야 한다.

SSH 설정 파일:

```text
C:\Users\Admin\.ssh\config
```

기존 설정:

```text
Host myUbuntu
  HostName 172.18.21.139
  User ubuntu
  IdentityFile ~/.ssh/id_ed25519
```

변경된 IP에 맞게 수정:

```text
Host myUbuntu
  HostName 172.18.27.40
  User ubuntu
  IdentityFile ~/.ssh/id_ed25519
```

---

## 6. 복구 확인

### SSH 접속 확인

```powershell
ssh myUbuntu
```

정상적으로 다음과 같이 접속되는지 확인한다.

```text
ubuntu@myUbuntu:~$
```

### Multipass shell 확인

```powershell
multipass shell myUbuntu
```

정상 접속되면 VM 복구가 완료된 것으로 판단한다.

---

## 7. VS Code Remote-SSH 재연결

SSH가 정상화된 후 VS Code에서 다시 연결한다.

```text
Ctrl + Shift + P
→ Remote-SSH: Connect to Host...
→ myUbuntu
```

그다음 작업 폴더를 다시 연다.

```text
/home/ubuntu/docker_lab4
```

---

## 8. 장애 원인 정리

이번 장애에서는 다음 현상이 확인되었다.

| 점검 항목 | 결과 |
|---|---|
| Multipass 상태 | Running |
| VM IP 접근 | 가능 |
| SSH 22번 포트 TCP 연결 | 가능 |
| SSH handshake 진행 | 비정상 |
| `multipass shell` | Timeout |
| VM 강제 재시작 후 | 정상 복구 |
| VM IP | 재시작 후 변경됨 |

최종적으로는 VM이 `Running` 상태였지만
실제 SSH 서비스 또는 VM 네트워크가 정상 응답하지 않는 상태였다.

---

## 9. 장애 대응 흐름

```text
VS Code 연결 실패
        ↓
ssh myUbuntu 확인
        ↓
ssh -vvv myUbuntu 확인
        ↓
TCP 연결은 성공하지만 SSH 응답 지연
        ↓
multipass shell myUbuntu 확인
        ↓
SSH timeout 발생
        ↓
VM 또는 VM 네트워크 문제 판단
        ↓
multipass stop myUbuntu
        ↓
종료되지 않으면
multipass stop --force myUbuntu
        ↓
multipass start myUbuntu
        ↓
multipass list로 새 IP 확인
        ↓
~/.ssh/config HostName 수정
        ↓
ssh myUbuntu 재확인
        ↓
VS Code Remote-SSH 재연결
```

---

## 10. 재발 방지 및 운영 포인트

1. `multipass list`의 `Running` 상태만 보고 VM이 정상이라고 판단하지 않는다.
2. SSH 문제가 발생하면 VS Code보다 먼저 `ssh myUbuntu`를 확인한다.
3. 필요하면 `ssh -vvv myUbuntu`로 어느 단계에서 멈추는지 확인한다.
4. `multipass shell`도 실패하면 VM 또는 Multipass 네트워크 문제를 의심한다.
5. VM 재시작 후 IP가 변경될 수 있으므로 반드시 `multipass list`를 다시 확인한다.
6. SSH config의 `HostName`이 현재 VM IP와 일치하는지 확인한다.
7. `multipass delete`, `purge`는 데이터 손실 위험이 있으므로 마지막 수단으로 사용한다.

---

## 핵심 요약

이번 장애는 VS Code 자체 문제가 아니라
Multipass VM 내부 SSH 응답 또는 VM 네트워크 이상으로 인해 발생하였다.

`multipass list`에서는 VM이 `Running` 상태였지만
`multipass shell`에서 SSH timeout이 발생했고,
VM을 강제 종료 후 재시작하면서 정상 상태로 복구되었다.

재시작 이후 VM IP가 변경되었기 때문에
Windows의 SSH config에 등록된 `HostName`도 새 IP로 수정해야 했다.
