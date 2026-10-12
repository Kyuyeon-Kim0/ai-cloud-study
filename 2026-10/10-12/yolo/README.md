# YOLOv8 객체 탐지 실습

Ultralytics YOLOv8을 사용해 이미지와 동영상에서 객체를 탐지하고, 추론 결과를 확인하는 학습 자료입니다. 기본 사전학습 모델 `yolov8n.pt`를 사용합니다.

## 파일 안내

| 파일 | 설명 |
|---|---|
| `yolo.ipynb` | `image.jpg`를 대상으로 추론하고, 탐지 상자와 클래스 정보를 확인하며 결과 이미지를 저장하는 노트북입니다. |
| `yolov8n_img.py` | 이미지 URL에서 이미지를 읽어 YOLOv8 추론을 수행하고 결과를 화면에 표시합니다. |
| `yolov8n_video.py` | `sample_video.mp4`를 대상으로 동영상 추론을 실행하고 화면에 표시합니다. |
| `yolov8n.pt` | YOLOv8n 사전학습 가중치 파일입니다. |
| `image.jpg` | 노트북에서 사용하는 입력 이미지입니다. |
| `sample_video.mp4` | 동영상 추론용 입력 파일입니다. |
| `result.jpg` | 노트북에서 시각화한 탐지 결과를 저장하는 이미지입니다. |
| `YOLOv8 모델 옵션·경량화·배포 가이드.md` | 모델 옵션, 시각화, 경량화 및 배포 방법을 정리한 참고 문서입니다. |

## 설치

Python 가상 환경에서 필요한 패키지를 설치합니다.

```powershell
python -m pip install ultralytics opencv-python matplotlib numpy jupyter
```

## 실행

`yolo.ipynb`를 Jupyter 또는 VS Code에서 열고 셀을 순서대로 실행합니다. 노트북은 현재 작업 폴더에 `image.jpg`와 `yolov8n.pt`가 있는 것을 기준으로 합니다. 추론 결과 이미지는 마지막 시각화 셀에서 `result.jpg`로 저장합니다.

이미지 스크립트:

```powershell
python yolov8n_img.py
```

이 스크립트는 코드에 지정된 이미지 URL에서 입력을 가져오므로 인터넷 연결이 필요합니다.

동영상 스크립트:

```powershell
python yolov8n_video.py
```

기본 코드는 추론 결과를 화면에 표시합니다. 결과 영상을 파일로 저장하려면 `yolov8n_video.py`에서 `show=True`를 `save=True`로 바꾸면 됩니다.

## 참고

모델을 불러올 때 파일 경로는 실행 중인 작업 폴더를 기준으로 해석됩니다. 다른 위치에서 실행한다면 `yolov8n.pt`, `image.jpg`, `sample_video.mp4`의 경로를 코드에 맞게 지정하세요.
