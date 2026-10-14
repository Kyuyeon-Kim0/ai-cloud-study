# AlexNet 전이 학습 이미지 분류

사전 학습된 AlexNet 모델을 사용해 이미지 4장을 ImageNet의 1,000개 클래스 중 하나로 분류하는 예제입니다. 모델의 가중치를 새로 학습시키지는 않고, 이미 학습된 모델을 불러와 추론합니다.

## 폴더 구성

```text
alexnet_image_classification/
├── transfer_test.py  # 이미지 전처리, 분류, 결과 표시
├── content/           # 분류할 이미지
│   ├── 추론cat.jpg
│   ├── 추론cat2.jpg
│   ├── 추론dog.jpg
│   └── 추론ship.jpg
└── README.md
```

## 설치

PowerShell에서 이 폴더로 이동한 뒤 필요한 패키지를 설치합니다.

```powershell
python -m pip install torch torchvision pillow matplotlib
```

## 실행

```powershell
python transfer_test.py
```

처음 실행할 때는 사전 학습된 AlexNet 가중치를 다운로드하므로 인터넷 연결이 필요할 수 있습니다. 실행하면 각 이미지의 텐서 크기, 예측 클래스 번호와 이름이 터미널에 출력되고 이미지가 표시됩니다.

## 다른 이미지 분류하기

분류할 이미지 파일을 `content` 폴더에 넣고, `transfer_test.py`의 `img_list`에 해당 파일 경로를 추가하세요. 입력 이미지는 RGB로 변환된 뒤 AlexNet 입력 크기인 224×224에 맞게 전처리됩니다.

ImageNet 1,000개 클래스 중 가장 높은 점수를 받은 항목 하나를 출력합니다. 결과는 모델의 예측이며 실제 정답과 다를 수 있습니다.
