# AlexNet 전이 학습 모델로 이미지 분류하기
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from PIL import Image
from torchvision import models, transforms

# 1. 사전 학습된 AlexNet 모델 불러오기
weights = models.AlexNet_Weights.IMAGENET1K_V1
model = models.alexnet(weights=weights)
model.eval()
classes = weights.meta["categories"]

# 2. ImageNet 모델 입력 규격에 맞게 이미지 전처리하기
preprocess = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet 채널별 평균
            std=[0.229, 0.224, 0.225],  # ImageNet 채널별 표준편차
        ),
    ]
)

# 3. 예측할 이미지 불러오기 (content 폴더의 로컬 파일)
content_dir = Path(__file__).resolve().parent / "content"
img_list = [
    content_dir / "추론cat.jpg",
    content_dir / "추론dog.jpg",
    content_dir / "추론ship.jpg",
    content_dir / "추론cat2.jpg",
]

for imgfile in img_list:
    img = Image.open(imgfile).convert("RGB")
    x = preprocess(img).unsqueeze(0)
    print("입력 텐서 크기:", x.shape)  # 모델 입력 형식: (1, 3, 224, 224)

    # 4. 이미지 분류 예측하기
    with torch.no_grad():
        outputs = model(x)
        _, predicted = outputs.max(1)

    class_index = predicted.item()
    print("예측 클래스 번호:", class_index)
    print("예측 클래스 이름:", classes[class_index])

    plt.figure(figsize=(3, 3))
    plt.axis("off")  # x축과 y축 숨기기
    plt.imshow(img)
    plt.show()
