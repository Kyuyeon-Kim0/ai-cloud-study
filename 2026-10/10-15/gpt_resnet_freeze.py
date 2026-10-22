
import os
import io
import json
import base64

import torch
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
from torchvision import models

# ==========================================
# 1. 환경 설정
# ==========================================
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
GPT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")

IMAGE_PATH = "testimg.jpg"

# ==========================================
# 2. ResNet18 로드
# ==========================================
weights = models.ResNet18_Weights.IMAGENET1K_V1
model = models.resnet18(weights=weights)
model.eval()

image = Image.open(IMAGE_PATH).convert("RGB")
x = weights.transforms()(image).unsqueeze(0)

# ==========================================
# 3. 레이어별 Feature Map 추출
# ==========================================
features = {}
hooks = []

layer_names = [
    "conv1", "layer1", "layer2",
    "layer3", "layer4"
]

def make_hook(name):
    def hook(module, inputs, output):
        features[name] = output.detach().cpu()
    return hook

for name in layer_names:
    layer = dict(model.named_modules())[name]
    hooks.append(layer.register_forward_hook(make_hook(name)))

with torch.no_grad():
    output = model(x)

for hook in hooks:
    hook.remove()

# ==========================================
# 4. Feature Map 이미지 생성
# ==========================================
def make_feature_image():
    fig, axes = plt.subplots(
        len(layer_names) + 1, 4,
        figsize=(12, 15)
    )

    # 원본 이미지
    axes[0, 0].imshow(image)
    axes[0, 0].set_title("Original")

    for ax in axes[0, 1:]:
        ax.axis("off")

    for row, name in enumerate(layer_names, 1):
        fmap = features[name][0]

        # 평균 활성화가 높은 채널 4개 선택
        scores = fmap.abs().mean(dim=(1, 2))
        top_idx = torch.topk(scores, 4).indices

        for col, channel_idx in enumerate(top_idx):
            channel = fmap[channel_idx].numpy()

            axes[row, col].imshow(
                channel, cmap="viridis"
            )
            axes[row, col].set_title(
                f"{name} / Ch {channel_idx.item()}"
            )

    for ax in axes.flat:
        ax.axis("off")

    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", dpi=120)
    plt.close(fig)

    return buffer.getvalue()

feature_image = make_feature_image()

with open("feature_maps.png", "wb") as f:
    f.write(feature_image)

# ==========================================
# 5. 레이어별 통계
# ==========================================
stats = {}

for name, fmap in features.items():
    stats[name] = {
        "shape": list(fmap.shape),
        "mean": round(fmap.mean().item(), 5),
        "std": round(fmap.std().item(), 5),
        "abs_mean": round(fmap.abs().mean().item(), 5),
        "zero_ratio": round(
            (fmap == 0).float().mean().item(), 5
        )
    }

# ==========================================
# 6. GPT 이미지 분석
# ==========================================
encoded = base64.b64encode(
    feature_image
).decode("utf-8")

prompt = f"""
너는 PyTorch 전이학습 전문가다.

ResNet18의 레이어별 Feature Map 이미지와
활성화 통계를 분석하라.

통계:
{json.dumps(stats, ensure_ascii=False, indent=2)}

목표:
1. 레이어별 특징 추출 상태 해석
2. 초기 동결 레이어 추천
3. 학습할 레이어 추천
4. 추천 근거 작성
5. 검증 실험 제안

주의:
- Feature Map만으로 최적의 동결 범위를
  확정할 수 없음을 명시한다.
- 색상이나 활성화가 강하다는 이유만으로
  특정 객체를 인식했다고 단정하지 않는다.
- 단일 이미지 분석이라는 한계를 반영한다.
- fc는 새 분류 작업에 맞게 교체한다고 가정한다.

반드시 아래 JSON 형식으로만 응답하라.

{{
  "analysis": {{
    "conv1": "분석",
    "layer1": "분석",
    "layer2": "분석",
    "layer3": "분석",
    "layer4": "분석"
  }},
  "freeze_layers": ["conv1", "bn1", "layer1"],
  "train_layers": ["layer2", "layer3", "layer4", "fc"],
  "reason": "추천 근거",
  "experiment": "검증 방법"
}}

freeze_layers와 train_layers는
분석 결과에 따라 변경할 수 있다.
"""

response = client.responses.create(
    model=GPT_MODEL,
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": prompt
                },
                {
                    "type": "input_image",
                    "image_url": (
                        "data:image/png;base64," + encoded
                    )
                }
            ]
        }
    ],
    text={"format": {"type": "json_object"}}
)

result = json.loads(response.output_text)

print("\n===== GPT 분석 결과 =====")
print(json.dumps(result, ensure_ascii=False, indent=2))

# ==========================================
# 7. GPT 추천 레이어 검증
# ==========================================
# 임의 레이어 이름을 허용하지 않도록 제한
valid_layers = {
    "conv1", "bn1", "layer1",
    "layer2", "layer3", "layer4", "fc"
}

freeze_layers = set(result["freeze_layers"])
train_layers = set(result["train_layers"])

if (
    freeze_layers & train_layers
    or freeze_layers | train_layers != valid_layers
    or "fc" not in train_layers
):
    raise ValueError("GPT 레이어 추천 형식이 올바르지 않습니다.")

# ==========================================
# 8. 추천 동결 범위 적용
# ==========================================
for param in model.parameters():
    param.requires_grad = False

for name in train_layers:
    layer = getattr(model, name)

    for param in layer.parameters():
        param.requires_grad = True

print("\n===== 동결 설정 결과 =====")

for name in sorted(valid_layers):
    layer = getattr(model, name)
    is_trainable = any(
        p.requires_grad for p in layer.parameters()
    )
    print(
        f"{name:8s}: "
        f"{'TRAIN' if is_trainable else 'FREEZE'}"
    )

# ==========================================
# 9. 분석 결과 저장
# ==========================================
with open("gpt_analysis.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n분석 완료!")
