
import torch
import matplotlib.pyplot as plt
from PIL import Image
from torchvision import models, transforms

# ==========================================
# 1. ResNet18 모델 준비
# ==========================================
weights = models.ResNet18_Weights.IMAGENET1K_V1
model = models.resnet18(weights=weights)
model.eval()

# ==========================================
# 2. 사용자 이미지 준비
# ==========================================
image = Image.open(r"C:\ai-starter\2026-10\10-15\testimg.jpg").convert("RGB")

transform = weights.transforms()
x = transform(image).unsqueeze(0)

# ==========================================
# 3. Feature Map 시각화 함수
# ==========================================
def show_feature(name, out, max_channels=8):
    fmap = out.squeeze(0).detach().cpu()
    num = min(max_channels, fmap.shape[0])

    fig, axes = plt.subplots(
        1, num, figsize=(16, 3)
    )

    if num == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        ax.imshow(fmap[i].numpy(), cmap="gray")
        ax.set_title(f"Channel {i}")
        ax.axis("off")

    fig.suptitle(
        f"{name} | Shape: {tuple(out.shape)}",
        fontsize=13
    )
    plt.tight_layout()
    plt.show()


# ==========================================
# 4. ResNet18 레이어 순서대로 실행
# ==========================================
with torch.no_grad():

    out = model.conv1(x)
    show_feature("conv1", out)

    out = model.bn1(out)
    out = model.relu(out)
    out = model.maxpool(out)

    out = model.layer1(out)
    show_feature("layer1", out)

    out = model.layer2(out)
    show_feature("layer2", out)

    out = model.layer3(out)
    show_feature("layer3", out)

    out = model.layer4(out)
    show_feature("layer4", out)

    # 최종 분류
    out = model.avgpool(out)
    out = torch.flatten(out, 1)
    out = model.fc(out)

# ==========================================
# 5. 분류 결과 TOP 5
# ==========================================
probabilities = torch.softmax(out[0], dim=0)
top_probs, top_indices = torch.topk(probabilities, 5)

print("\n===== Prediction TOP 5 =====")

for prob, idx in zip(top_probs, top_indices):
    print(
        f"{weights.meta['categories'][idx]}: "
        f"{prob.item() * 100:.2f}%"
    )
