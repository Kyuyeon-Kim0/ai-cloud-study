# ai-cloud-study

AI 서비스·클라우드 엔지니어링 실무 학습 기록입니다.

학습한 내용을 날짜별로 정리하고, 실습 코드와 프로젝트 결과물을 관리합니다.

## 📚 학습 기록

### 2026년 9월 — IT 인프라 · 네트워크 · Docker

| 날짜 | 학습 내용 |
|---|---|
| [09-09 (수)](2026-09/09-09/README.md) | PowerShell 기초, 파일·폴더 관리, 시스템 점검 |
| [09-10 (목)](2026-09/09-10/README.md) | 네트워크·URL, JSON·XML, 공공데이터 API |
| [09-11 (금)](2026-09/09-11/README.md) | HTML·CSS, OpenCV·MediaPipe 얼굴 랜드마크, 눈 불꽃 합성 |
| [09-14 (월)](2026-09/09-14/README.md) | Python 시스템 자원 측정, OpenCV·Pillow 이미지·영상 처리 |
| [09-15 (화)](2026-09/09-15/README.md) | CSV·JSON 데이터 처리, Pandas, SQL 기초 |
| [09-16 (수)](2026-09/09-16/README.md) | Flask·FastAPI, OpenAI API, 모니터링 대시보드 |
| [09-23 (수)](2026-09/09-23/README.md) | Linux 프로세스·포트·트래픽 분석, Wireshark |
| [09-28 (월)](2026-09/09-28/README.md) | OSI 계층, ARP·MAC, VLAN, Packet Tracer |
| [09-29 (화)](2026-09/09-29/README.md) | 네트워크 장애 분석, 패킷 분석, OSI 상위 계층 |
| [09-30 (수)](2026-09/09-30/README.md) | Docker 이미지·컨테이너, Docker Compose |

### 2026년 10월 — 클라우드 · API · AI

| 날짜 | 학습 내용 |
|---|---|
| [10-01 (목)](2026-10/10-01/) | Multipass VM SSH 및 K3s Kubernetes API 장애 분석·복구 |
| [10-02 (금)](2026-10/10-02/README.md) | FastAPI·Docker·K3s 배포, ConfigMap·Secret, NodePort |
| [10-06 (화)](2026-10/10-06/README.md) | Python 모듈·클래스, CSV 매출 집계, 도구 레지스트리·CLI |
| [10-07 (수)](2026-10/10-07/) | Python Tool Registry, 비동기 웹 프레임워크, FastAPI·MySQL 웹서비스 |
| [10-08 (목)](2026-10/10-08/README.md) | MCP 서버·AI Agent·Tool Registry, FastAPI·MySQL 재고 관리 |
| [10-12 (월)](2026-10/10-12/README.md) | LLM API·LangChain·에이전트, 임베딩 비교, YOLOv8 객체 탐지·회의실 분석 |
| [10-13 (화)](2026-10/10-13/README.md) | YOLOv8 Pose 키포인트 추론, 회의실 객체 분석, GPT 보고서·제조 공정 영상 분석 |


### 이후 학습 일정 (예정)

| 날짜 | 예정 주제 |
|---|---|
| 10-14 (수) | Hugging Face, AI 모델 활용 |
| 10-15 (목) | 전이학습, 컴퓨터 비전 모델 활용 (마지막 학습일) |

## 🛠️ 주요 기술

| 분야 | 기술 |
|---|---|
| Language | Python, PowerShell, SQL |
| Web / API | HTML, CSS, FastAPI, Flask, REST API |
| Database | MySQL, CSV, JSON |
| Infrastructure | Linux, SSH, Network, Nginx |
| Cloud / DevOps | Docker, Docker Compose, Kubernetes(K3s), GitHub Actions |
| AI / Data | NumPy, Pandas, OpenCV, YOLO, Hugging Face |
| AI Agent | OpenAI API, LangChain, MCP |
| Tools | Git, GitHub, VS Code, Wireshark, Packet Tracer |

## 📝 정리 규칙

- 월별 폴더는 `YYYY-MM`, 날짜 폴더는 `MM-DD`로 작성합니다.
- 날짜별 `README.md`에 학습 내용, 실습 설명, 실행 방법을 기록합니다.
- 짧은 실습은 날짜 폴더에 직접 저장합니다.
- 여러 파일로 구성된 실습은 주제별 하위 폴더에 보관합니다.
- 코드의 재사용성과 확장성을 고려하여 기능별로 모듈화합니다.
- API Key, DB 접속 정보 등 민감한 설정은 `.env`로 관리합니다.
- 가상환경, 캐시, 로그, 비밀키는 Git 커밋에서 제외합니다.
- 프로젝트 결과물과 오류 해결 과정도 함께 기록합니다.

## 🎯 학습 목표

1. Linux 및 네트워크 인프라 이해
2. Python 기반 자동화 및 API 개발
3. Docker·Kubernetes 기반 서비스 배포
4. AI 모델과 클라우드 서비스 연동
5. 모니터링 및 장애 진단 자동화
6. AI Agent·MCP 기반 서비스 구현
