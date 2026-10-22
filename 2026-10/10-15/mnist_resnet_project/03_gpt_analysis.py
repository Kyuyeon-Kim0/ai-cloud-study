
import os
import json
import base64

from pathlib import Path
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

# ==========================================
# 1. 환경 설정
# ==========================================
load_dotenv()

OUTPUT_DIR = Path("outputs")
IMAGE_PATH = OUTPUT_DIR / "feature_maps.png"
STATS_PATH = OUTPUT_DIR / "feature_stats.json"
RESULT_PATH = OUTPUT_DIR / "freeze_analysis.json"

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

client = OpenAI()

# ==========================================
# 2. GPT 응답 구조 정의
# ==========================================
LayerName = Literal[
    "conv1", "bn1", "layer1",
    "layer2", "layer3", "layer4", "fc"
]

class LayerAnalysis(BaseModel):
    layer: LayerName
    observation: str
    interpretation: str

class FreezeRecommendation(BaseModel):
    task: str
    analyses: list[LayerAnalysis]

    freeze_layers: list[LayerName]
    train_layers: list[LayerName]

    reason: str
    limitations: str
    validation_plan: str

# ==========================================
# 3. 기존 결과 파일 확인
# ==========================================
for path in [IMAGE_PATH, STATS_PATH]:
    if not path.exists():
        raise FileNotFoundError(
            f"파일이 없습니다: {path}"
        )

# ==========================================
# 4. Feature Map 통계 읽기
# ==========================================
with open(STATS_PATH, "r", encoding="utf-8") as f:
    stats = json.load(f)

# ==========================================
# 5. 이미지 Base64 변환
# ==========================================
def encode_image(path: Path) -> str:
    """이미지를 GPT API 전송 형식으로 변환"""

    encoded = base64.b64encode(
        path.read_bytes()
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"

image_url = encode_image(IMAGE_PATH)

# ==========================================
# 6. GPT 분석 프롬프트
# ==========================================
prompt = f"""
당신은 PyTorch, ResNet18, 전이학습 전문가입니다.

[작업 목표]
MNIST 손글씨 숫자 0~9를 분류하기 위한
ResNet18의 초기 동결 범위를 추천하세요.

[현재 모델]
- ResNet18
- ImageNet 사전학습 가중치
- 입력: MNIST 흑백 이미지를 RGB로 변환
- 최종 출력: 10개 클래스
- 현재 이미지는 MNIST 샘플 1장
- 아직 MNIST 재학습 전

[Feature Map 통계]
{json.dumps(stats, ensure_ascii=False, indent=2)}

[분석 요청]
1. conv1, layer1, layer2, layer3, layer4의
   시각적 특징과 통계를 분석하세요.

2. ImageNet 자연 이미지와 MNIST 손글씨
   이미지의 도메인 차이를 고려하세요.

3. 초기 동결 레이어와 재학습 레이어를
   추천하세요.

4. 레이어별 관찰 사실과 해석을 구분하세요.

5. 단일 이미지로 최적의 동결 위치를
   확정할 수 없다는 한계를 명시하세요.

6. 실제 검증 데이터로 비교할 실험을
   제안하세요.

[레이어 규칙]
- 사용 가능한 레이어:
  conv1, bn1, layer1, layer2, layer3, layer4, fc
- fc는 반드시 train_layers에 포함하세요.
- 모든 레이어는 freeze 또는 train 중
  정확히 한쪽에만 포함하세요.
- conv1과 bn1은 동일한 동결 상태를
  유지하세요.
- 학습 범위는 연속적인 후반 레이어로
  설정하세요.
- fc는 새 10개 클래스 출력으로 교체할
  예정입니다.
- 추천은 가설이며 확정적인 최적해가
  아닙니다.
"""

# ==========================================
# 7. GPT 비전 분석
# ==========================================
print("GPT Feature Map 분석 시작...")

response = client.responses.parse(
    model=MODEL_NAME,
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
                    "image_url": image_url,
                    "detail": "high"
                }
            ]
        }
    ],
    text_format=FreezeRecommendation
)

result = response.output_parsed

if result is None:
    raise RuntimeError(
        "GPT의 구조화된 분석 결과를 받지 못했습니다."
    )

# ==========================================
# 8. 레이어 추천 검증
# ==========================================
layer_order = [
    "conv1", "bn1", "layer1",
    "layer2", "layer3", "layer4", "fc"
]

freeze_set = set(result.freeze_layers)
train_set = set(result.train_layers)

if freeze_set & train_set:
    raise ValueError("동결/학습 레이어가 중복됩니다.")

if freeze_set | train_set != set(layer_order):
    raise ValueError("누락되거나 잘못된 레이어가 있습니다.")

if "fc" not in train_set:
    raise ValueError("FC는 반드시 학습해야 합니다.")

if ("conv1" in train_set) != ("bn1" in train_set):
    raise ValueError("conv1과 bn1의 상태가 다릅니다.")

# 앞부분 동결 + 뒷부분 학습인지 확인
train_started = False

for name in layer_order:
    if name in train_set:
        train_started = True
    elif train_started:
        raise ValueError(
            "학습 레이어는 연속된 후반부여야 합니다."
        )

# ==========================================
# 9. JSON 저장
# ==========================================
result_dict = result.model_dump()

with open(
    RESULT_PATH, "w", encoding="utf-8"
) as f:
    json.dump(
        result_dict,
        f,
        ensure_ascii=False,
        indent=4
    )

# ==========================================
# 10. 결과 출력
# ==========================================
print("\n===== 레이어별 분석 =====")

for item in result.analyses:
    print(f"\n[{item.layer}]")
    print("관찰:", item.observation)
    print("해석:", item.interpretation)

print("\n===== GPT 추천 =====")
print("동결 레이어:", result.freeze_layers)
print("학습 레이어:", result.train_layers)
print("추천 이유:", result.reason)
print("분석 한계:", result.limitations)
print("검증 계획:", result.validation_plan)

print(f"\nJSON 저장 완료: {RESULT_PATH}")
