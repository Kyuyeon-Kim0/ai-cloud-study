# 2026-09-30 (수) Docker 실습 기록

## 학습 주제

- Docker 이미지와 컨테이너의 기본 개념
- Dockerfile로 Python API와 Nginx 웹 페이지 이미지 만들기
- 포트 매핑과 사용자 정의 네트워크를 이용한 컨테이너 통신
- Docker Compose로 여러 서비스를 한 번에 실행·관리하기
- 볼륨으로 컨테이너 밖의 데이터를 연결하기

## 실습 구성

| 구분 | 내용 | 시작하기 |
| --- | --- | --- |
| Docker Lab 2 | API와 웹 사이트를 각각 이미지로 빌드하고 컨테이너로 실행 | [README](docker_lab2/README.md) |
| Docker Lab 3 | Compose 파일로 API와 웹 사이트를 함께 실행 | [README](docker_lab3/README.md) |
| Compose 옵션 정리 | 자주 쓰는 Docker Compose 명령어와 옵션 참고 자료 | [HTML 문서](<Docker Compose 명령어별 옵션 정리.html>) |
| 교안 | Docker 시작하기, 이미지 만들기, Docker Compose 교안 | [교안 폴더](교안/) |

## 실습 순서

1. [Docker 시작하기 교안](<교안/Part1. docker_시작하기_교안.html>)으로 이미지·컨테이너·포트 개념을 확인합니다.
2. [docker_lab2](docker_lab2/)에서 API와 사이트 이미지를 각각 빌드하고 `5000`, `8080` 포트로 실행합니다.
3. `labnet` 사용자 정의 네트워크에서 서비스 이름 `api`로 API 컨테이너에 접근해 봅니다.
4. [docker_lab3](docker_lab3/)에서 `docker compose up -d --build`로 두 서비스를 함께 실행합니다.
5. [Compose 교안](<교안/Part3. docker_compose_교안.html>)과 [명령어 옵션 정리](<Docker Compose 명령어별 옵션 정리.html>)로 운영 명령을 복습합니다.

## 빠른 실행: Docker Compose

```powershell
cd docker_lab3
docker compose up -d --build
docker compose ps
```

- 웹 대시보드: <http://localhost:8080>
- API 요약: <http://localhost:5000/api/summary>

정리할 때는 다음 명령을 실행합니다.

```powershell
docker compose down
```

## 핵심 파일

```text
09-30/
├── docker_lab2/       # 개별 Dockerfile·컨테이너 실습
├── docker_lab3/       # Docker Compose 실습
├── 교안/              # 수업 교안
└── Docker Compose 명령어별 옵션 정리.html
```

## 준비물

- Docker Desktop (Docker Compose v2 포함)
- Windows PowerShell 또는 VS Code 터미널
- 웹 브라우저
