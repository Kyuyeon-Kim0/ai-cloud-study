# MediaPipe 눈 불꽃 합성

학습 날짜: 2026-09-11 (금)

웹캠에서 얼굴 한 명을 추적하고, `a.png` 이미지를 양쪽 눈 위에 실시간 합성하는 Python 프로그램입니다. 이미지가 RGB 형식이고 흰 배경이어도 실행 중 자동으로 투명 처리합니다.

## 준비 사항

- Windows 10/11
- 웹캠
- Python 3.10~3.12 권장

## 폴더 구성

```text
mediapipe_eye_fire/
├─ eye_fire.py
├─ a.png
├─ requirements.txt
├─ TASK.md
└─ README.md
```

## 설치 및 실행

PowerShell에서 프로젝트 폴더로 이동한 뒤 실행합니다.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python eye_fire.py
```

PowerShell 실행 정책 오류가 나면 현재 창에서만 다음 명령을 먼저 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

영상 창에서 Q 또는 ESC를 누르면 종료됩니다.

## 실행 옵션

```powershell
# 두 번째 카메라 사용
python eye_fire.py --camera 1

# 불꽃 크기 조절(기본값 2.2)
python eye_fire.py --scale 3.0

# 다른 PNG 사용
python eye_fire.py --image my_image.png
```

## 문제 해결

| 증상 | 확인할 내용 |
|---|---|
| 웹캠을 열 수 없음 | Windows 카메라 권한을 켜고 Zoom·Teams 등을 종료한 뒤 재시도 |
| 검은 화면 | `python eye_fire.py --camera 1`로 다른 카메라 번호 시도 |
| `mediapipe` 설치 실패 | Python 3.11 64비트 환경 사용 권장 |
| `a.png`를 읽을 수 없음 | `a.png`가 `eye_fire.py`와 같은 폴더에 있는지 확인 |
| 불꽃이 너무 크거나 작음 | `--scale` 값을 1.5~3.0 범위에서 조정 |

## 처리 순서

1. OpenCV가 웹캠 프레임을 읽습니다.
2. MediaPipe Face Mesh가 얼굴과 눈 끝점을 찾습니다.
3. 두 눈의 폭과 각도에 맞춰 불꽃 크기와 회전을 계산합니다.
4. 흰 배경을 투명 처리한 불꽃을 각 눈의 중심에 합성합니다.
5. 합성된 영상을 화면에 표시합니다.
