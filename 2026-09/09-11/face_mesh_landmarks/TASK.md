# Codex 작업지시서

## 작업 목적

- MediaPipe Face Mesh로 얼굴 랜드마크 연결선과 번호를 표시한다.
- 웹캠과 이미지 파일 입력을 모두 지원한다.
- 실행 오류를 확인하고, 필요한 경우 최소 범위만 수정한다.

## 대상 파일

- 실행 코드: `face_mesh_landmarks.py`
- 패키지 목록: `requirements.txt`
- 사용 안내: `README.md`

## 실행 환경

- 권장 Python: 3.10~3.12
- 운영체제: Windows 기준
- 실행 폴더: 이 파일이 있는 프로젝트 폴더

## 작업 순서

1. `README.md`, `requirements.txt`, `face_mesh_landmarks.py`의 존재 여부만 확인한다.
2. 가상환경을 만들고 필요한 패키지를 설치한다.
3. 먼저 `python face_mesh_landmarks.py --help`로 기본 실행 여부를 확인한다.
4. 이미지가 제공되면 이미지 모드로 검사한다.
5. 이미지가 없으면 웹캠 모드로 실행한다.
6. 얼굴 연결선과 번호가 표시되는지 확인한다.
7. 오류가 있으면 원인을 확인하고 최소 수정 후 한 번 더 실행한다.
8. 변경 파일, 실행 명령, 확인 결과를 짧게 보고한다.

## 실행 명령

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python face_mesh_landmarks.py --help
python face_mesh_landmarks.py
```

이미지 파일 검사:

```powershell
python face_mesh_landmarks.py --image face.jpg --output result.jpg
```

## 오류 처리 규칙

- 오류 메시지를 먼저 읽고 원인을 한 줄로 정리한다.
- 임의로 새 라이브러리를 추가하지 않는다.
- 패키지 오류는 `requirements.txt`와 현재 Python 버전을 먼저 확인한다.
- 카메라 오류는 카메라 번호, 다른 앱의 카메라 사용 여부, Windows 권한을 확인한다.
- 이미지 오류는 경로와 파일 존재 여부를 확인한다.
- 코드 수정이 필요하면 관련 부분만 수정한다.
- 동일 오류가 재현되고 수정 근거가 명확할 때만 기존 파일을 덮어쓴다.
- 사용자 원본 이미지와 정상 결과 파일은 덮어쓰지 않는다.
- 수정 후 `py_compile` 또는 `--help`와 실제 실행을 다시 확인한다.
- 해결되지 않으면 추측으로 반복 수정하지 말고 오류 전문과 시도한 내용을 보고한다.

## 토큰 효율화 규칙

- 처음에는 대상 파일만 읽고 다른 폴더 전체를 탐색하지 않는다.
- 같은 파일을 변경 없이 반복해서 읽지 않는다.
- 긴 로그는 전체를 복사하지 않고 핵심 오류와 마지막 부분만 확인한다.
- 정상 동작하는 코드는 다시 작성하지 않는다.
- 설명보다 실행·검증을 우선하고 완료 보고는 짧게 작성한다.
- 한 번에 한 원인만 수정해 결과를 확인한다.

## 변경 제한

- `.venv` 이외의 시스템 설정을 영구 변경하지 않는다.
- 요청 없이 API 서버, GUI, 데이터베이스를 추가하지 않는다.
- `face_mesh_landmarks.py`의 기존 옵션 이름을 임의로 바꾸지 않는다.
- 불필요한 파일 생성 및 대규모 리팩터링을 하지 않는다.

## 완료 조건

- 패키지 설치가 완료된다.
- `--help` 명령이 오류 없이 실행된다.
- 웹캠 또는 이미지에서 얼굴 랜드마크가 표시된다.
- 이미지 모드에서는 지정한 결과 파일이 생성된다.
- 변경 내용과 남은 오류를 사용자에게 짧게 보고한다.
