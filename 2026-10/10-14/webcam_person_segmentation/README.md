# 웹캠 인물 분할 및 배경 교체

PyTorch의 사전 학습된 DeepLabV3 모델로 웹캠 영상에서 사람을 분할하고, 사람 뒤의 배경을 `back.jpg` 이미지로 교체하는 Python 프로그램입니다.

## 파일 구성

```text
webcam_person_segmentation/
├── main.py       # 웹캠 처리 및 배경 합성 코드
├── back.jpg      # 합성에 사용할 배경 이미지
└── README.md
```

`back.jpg`를 다른 이미지로 교체하면 해당 이미지가 새 배경으로 사용됩니다. 이미지 파일명은 `back.jpg`로 유지해 주세요.

## 설치

프로젝트 폴더에서 PowerShell을 열고 가상환경을 만든 뒤 필요한 패키지를 설치합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch torchvision opencv-python pillow numpy
```

## 실행

```powershell
python main.py
```

처음 실행할 때는 사전 학습된 모델 가중치를 다운로드할 수 있도록 인터넷 연결이 필요합니다. 기본 설정은 CUDA GPU가 있으면 GPU를 사용하고, 없으면 CPU로 실행합니다. CPU에서는 영상 처리 속도가 느릴 수 있습니다.

웹캠이 열리지 않으면 다른 프로그램이 카메라를 사용 중인지, Windows의 카메라 권한이 허용되어 있는지 확인하세요. 실행 중에는 원본 영상과 배경 합성 결과가 각각 표시됩니다. `q` 키를 누르면 종료합니다.
