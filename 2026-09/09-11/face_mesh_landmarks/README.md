# MediaPipe 얼굴 랜드마크 표시기

학습 날짜: 2026-09-11 (금)

얼굴에 Face Mesh 연결선과 랜드마크 번호를 표시하는 프로젝트입니다.
직접 실행할 때는 아래 순서를 따르고, Codex에 맡길 때는 `TASK.md`를 읽도록 지시하세요.

## 전체 작업 순서

1. 프로젝트 폴더를 연다.
2. Python 버전을 확인한다.
3. 가상환경을 만들고 활성화한다.
4. 필요한 패키지를 설치한다.
5. `--help`로 프로그램 로딩을 확인한다.
6. 웹캠 또는 이미지 모드로 실행한다.
7. 연결선과 번호를 확인한다.
8. 문제가 있으면 아래 오류 해결 순서로 점검한다.

## 1. 프로젝트 폴더로 이동

```powershell
cd mediapipe_face_mesh
python --version
```

Python 3.10~3.12 환경을 권장합니다.

## 2. 가상환경 생성 및 활성화

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

PowerShell에서 가상환경 실행이 차단되면 현재 창에서만 다음 명령을 먼저 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 3. 패키지 설치

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. 기본 점검

```powershell
python face_mesh_landmarks.py --help
```

도움말이 표시되면 프로그램과 패키지가 정상적으로 준비된 것입니다.

## 5. 웹캠 실행

```powershell
python face_mesh_landmarks.py
```

- `Q`: 종료
- `S`: 현재 화면을 `result.jpg`로 저장

## 6. 이미지 파일 실행

```powershell
python face_mesh_landmarks.py --image face.jpg --output result.jpg
```

`face.jpg`는 실제 입력 이미지의 파일명으로 바꾸세요.

## 7. 자주 쓰는 옵션

```powershell
# 번호를 표시하지 않음
python face_mesh_landmarks.py --no-numbers

# 번호가 너무 겹치면 5개마다 하나씩 표시
python face_mesh_landmarks.py --number-step 5

# 두 얼굴까지 인식
python face_mesh_landmarks.py --max-faces 2
```

## 8. 오류 해결 순서

| 증상 | 먼저 확인할 내용 |
| --- | --- |
| `No module named mediapipe` | 가상환경 활성화 후 `pip install -r requirements.txt` 재실행 |
| 웹캠이 열리지 않음 | 다른 카메라 앱 종료, Windows 카메라 권한, `--camera 1` 확인 |
| 이미지를 읽을 수 없음 | 이미지 파일명, 확장자, 현재 폴더 확인 |
| 번호가 너무 겹침 | `--number-step 5`처럼 간격 확대 |
| 얼굴이 인식되지 않음 | 밝은 정면 사진 사용, 얼굴 크기와 조명 확인 |

Codex에서 실행할 때 요청 예시:

```text
TASK.md를 읽고 지시된 순서대로 실행해 줘.
오류가 나면 원인을 먼저 확인하고 최소 범위만 수정해 줘.
```
