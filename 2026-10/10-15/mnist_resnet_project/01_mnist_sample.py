
import torch
import matplotlib.pyplot as plt

from pathlib import Path
from torchvision import datasets

# ==========================================
# 1. 저장 폴더 생성
# ==========================================
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. MNIST 데이터셋 다운로드
# ==========================================
train_dataset = datasets.MNIST(
    root=str(DATA_DIR),
    train=True,
    download=True
)

test_dataset = datasets.MNIST(
    root=str(DATA_DIR),
    train=False,
    download=True
)

print("===== MNIST 데이터 정보 =====")
print(f"훈련 데이터: {len(train_dataset):,}장")
print(f"테스트 데이터: {len(test_dataset):,}장")

# ==========================================
# 3. 샘플 이미지 한 장 추출
# ==========================================
SAMPLE_INDEX = 0

image, label = train_dataset[SAMPLE_INDEX]

print("\n===== 샘플 정보 =====")
print(f"정답 숫자: {label}")
print(f"이미지 크기: {image.size}")
print(f"이미지 모드: {image.mode}")

# ==========================================
# 4. 샘플 이미지 저장
# ==========================================
save_path = OUTPUT_DIR / "sample.png"

image.save(save_path)

print(f"이미지 저장 완료: {save_path}")

# ==========================================
# 5. 이미지 시각화
# ==========================================
plt.figure(figsize=(5, 5))

plt.imshow(image, cmap="gray")
plt.title(f"MNIST Sample - Label: {label}")
plt.axis("off")

plt.show()
