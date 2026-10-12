# YOLO 회의실 분석 에이전트

회의실 사진을 YOLOv8으로 분석해 사람·의자·테이블을 탐지하고, 인원수에 따라 공간 상태를 분류하는 Python 실습 프로젝트입니다. 설정에 따라 OpenAI 에이전트가 탐지 집계 결과를 바탕으로 요약과 활용 제안을 작성합니다.

## 동작 흐름

1. 입력 폴더에서 JPG, JPEG, PNG, WEBP 이미지를 읽습니다.
2. YOLO로 사람, 의자, 테이블을 탐지하고 바운딩 박스 이미지를 저장합니다.
3. 탐지된 사람 수를 기준으로 회의실 상태를 분류합니다.
4. `ENABLE_AGENT=true`이면 탐지 집계 정보만 OpenAI API에 전달해 구조화된 분석 보고서를 생성합니다.
5. 전체 결과를 JSON과 CSV 파일로 저장합니다.

## 폴더 구성

| 경로 | 설명 |
|---|---|
| `app/` | 이미지 분석, 에이전트 보고서, 설정, 검증 및 CLI 코드 |
| `images/` | 분석할 회의실 이미지 입력 폴더 |
| `outputs/` | 탐지 이미지와 JSON·CSV 결과가 생성되는 폴더 |
| `.env.example` | 환경 변수 설정 예시 |
| `requirements.txt` | Python 패키지 목록 |

## 설치 및 설정 (Windows PowerShell)

프로젝트 폴더에서 가상 환경을 만들고 패키지를 설치합니다.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`.env.example`을 복사해 `.env`를 만들고, 에이전트 기능을 사용할 경우 `OPENAI_API_KEY`를 설정합니다.

```powershell
Copy-Item .env.example .env
```

`.env`가 이미 있다면 복사 명령은 생략하고 기존 파일을 수정하세요. 주요 설정은 다음과 같습니다.

| 변수 | 기본값 | 설명 |
|---|---|---|
| `OPENAI_API_KEY` | 없음 | 에이전트 보고서 생성에 필요한 API 키 |
| `OPENAI_MODEL` | `.env.example`: `gpt-5.6-luna` | 보고서 생성에 사용할 모델 |
| `YOLO_MODEL` | `yolov8n.pt` | YOLO 가중치 파일 또는 모델 이름 |
| `YOLO_CONF` | `0.35` | 탐지 신뢰도 임계값 (0 초과, 1 이하) |
| `SMALL_GROUP_MAX` | `3` | 이 인원 이하를 `소규모`로 분류 |
| `CROWDED_MIN` | `7` | 이 인원 이상을 `혼잡`으로 분류 |
| `ENABLE_AGENT` | `true` | OpenAI 에이전트 보고서 생성 여부 |

에이전트 호출 없이 YOLO 분류만 실행하려면 `.env`에서 `ENABLE_AGENT=false`로 설정할 수 있습니다.

## 사용법

회의실 사진을 `images/`에 넣고 프로젝트 폴더에서 실행합니다.

```powershell
python -m app.main --input images --output outputs
```

입력 및 출력 폴더는 인자로 바꿀 수 있습니다.

```powershell
python -m app.main --input "C:\path\to\photos" --output "C:\path\to\results"
```

지원 확장자는 `.jpg`, `.jpeg`, `.png`, `.webp`이며 이미지 한 장의 최대 크기는 15 MB입니다. 지원 형식의 파일이 없으면 분석 없이 종료합니다.

## 결과 파일

- `outputs/<이미지이름>_boxed.jpg`: 탐지 상자를 그린 이미지
- `outputs/results.json`: 객체별 탐지 상자, 신뢰도, 상태, 경고 및 에이전트 보고서
- `outputs/summary.csv`: 이미지별 사람·의자·테이블 수, 상태 및 UTC 처리 시각

## 분석 및 개인정보 관련 안내

- 인원수와 상태는 Python 코드가 YOLO 탐지 결과로 정하며, 에이전트는 이를 바꾸지 않고 설명과 제안만 작성합니다.
- 원본 이미지는 OpenAI API에 보내지 않습니다. 보고서 생성에는 이미지명, 객체 수, 인원수, 상태, 안내 문구만 전달됩니다.
- `비어 있음`은 사진에서 사람을 탐지하지 못했다는 뜻이며, 실제 공실이나 예약 가능 상태를 보장하지 않습니다. 가림이나 겹침으로 탐지 결과가 달라질 수 있습니다.
- 한 장의 사진으로 신원이나 민감한 속성, 시간대별 이용 추세를 판단하지 않습니다.
- 에이전트 호출이 실패해도 규칙 기반 탐지 결과는 저장되며, 실패 내용은 해당 JSON 결과에 기록됩니다.
- `.env`, 개인 이미지 및 분석 결과를 공개 저장소에 올리지 마세요.
