
import json
import torch
import matplotlib.pyplot as plt

from pathlib import Path
from PIL import Image
from torchvision import models

# ==========================================
# 1. 기본 설정
# ==========================================
IMAGE_PATH = Path("outputs/sample.png")
OUTPUT_DIR = Path("outputs")

OUTPUT_DIR.mkdir(exist_ok=True)

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print("사용 장치:", DEVICE)

# ==========================================
# 2. ResNet18 모델 불러오기
# ==========================================
weights = models.ResNet18_Weights.IMAGENET1K_V1

model = models.resnet18(
    weights=weights
).to(DEVICE)

model.eval()

# ==========================================
# 3. MNIST 이미지 불러오기
# ==========================================
# MNIST는 흑백 1채널
# ResNet18은 RGB 3채널 입력 필요

image = Image.open(IMAGE_PATH).convert("RGB")

# ImageNet 사전학습 모델 전처리
transform = weights.transforms()

x = transform(image).unsqueeze(0).to(DEVICE)

print("입력 Tensor:", x.shape)

# ==========================================
# 4. Feature Map 저장용 Hook
# ==========================================
features = {}
hooks = []

layer_names = [
    "conv1",
    "layer1",
    "layer2",
    "layer3",
    "layer4"
]

def create_hook(name):
    """레이어의 출력 특징 맵 저장"""

    def hook(module, inputs, output):
        features[name] = output.detach().cpu()

    return hook

for name in layer_names:
    layer = getattr(model, name)

    handle = layer.register_forward_hook(
        create_hook(name)
    )

    hooks.append(handle)

# ==========================================
# 5. 모델 추론
# ==========================================
with torch.no_grad():
    output = model(x)

# Hook 제거
for handle in hooks:
    handle.remove()

# ==========================================
# 6. Feature Map 통계 계산
# ==========================================
stats = {}

for name, fmap in features.items():

    stats[name] = {
        "shape": list(fmap.shape),
        "mean": round(fmap.mean().item(), 5),
        "std": round(fmap.std().item(), 5),
        "abs_mean": round(
            fmap.abs().mean().item(), 5
        ),
        "zero_ratio": round(
            (fmap == 0).float().mean().item(), 5
        )
    }

    print(
        f"{name:8s} -> {tuple(fmap.shape)}"
    )

# JSON 파일 저장
with open(
    OUTPUT_DIR / "feature_stats.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        stats,
        f,
        indent=4,
        ensure_ascii=False
    )

# ==========================================
# 7. Feature Map 시각화
# ==========================================
# 레이어마다 활성화 크기가 큰
# 상위 8개 채널을 선택

MAX_CHANNELS = 8

fig, axes = plt.subplots(
    6,
    MAX_CHANNELS,
    figsize=(18, 15)
)

# 첫 번째 행: 원본 이미지
axes[0, 0].imshow(image)
axes[0, 0].set_title("Original MNIST")

for col in range(1, MAX_CHANNELS):
    axes[0, col].axis("off")

# 각 레이어 특징 맵
for row, name in enumerate(layer_names, start=1):

    fmap = features[name][0]

    # 채널별 평균 절댓값 활성화
    scores = fmap.abs().mean(dim=(1, 2))

    # 활성화가 높은 채널 선택
    num = min(MAX_CHANNELS, fmap.shape[0])

    top_channels = torch.topk(
        scores,
        k=num
    ).indices

    for col in range(MAX_CHANNELS):

        ax = axes[row, col]

        if col >= num:
            ax.axis("off")
            continue

        channel_idx = top_channels[col].item()

        feature = fmap[channel_idx].numpy()

        ax.imshow(
            feature,
            cmap="viridis",
            interpolation="nearest"
        )

        ax.set_title(
            f"{name} / Ch {channel_idx}",
            fontsize=9
        )

        ax.axis("off")

plt.suptitle(
    "MNIST - ResNet18 Feature Maps",
    fontsize=18
)

plt.tight_layout()

# ==========================================
# 8. 결과 저장
# ==========================================
save_path = OUTPUT_DIR / "feature_maps.png"

plt.savefig(
    save_path,
    dpi=200,
    bbox_inches="tight"
)

plt.show()

print("\n===== 저장 완료 =====")
print("Feature Map:", save_path)
print("통계 JSON:", OUTPUT_DIR / "feature_stats.json")
