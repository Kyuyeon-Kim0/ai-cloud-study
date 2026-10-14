import json
from pathlib import Path

import requests
import torch
from PIL import Image, ImageDraw, ImageFont
from transformers import Owlv2ForObjectDetection, Owlv2Processor


MODEL_ID = "google/owlv2-base-patch16-ensemble"
IMAGE_URL = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/zero-sh-obj-detection_1.png"
OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "owlv2_detections.json"
ANNOTATED_OUTPUT = Path(__file__).resolve().parents[1] / "outputs" / "owlv2_annotated.png"
VISUAL_THRESHOLD = 0.3


def main():
    response = requests.get(IMAGE_URL, timeout=60)
    response.raise_for_status()
    image_path = Path(__file__).resolve().parent / "coco_sample.jpg"
    image_path.write_bytes(response.content)
    image = Image.open(image_path).convert("RGB")

    processor = Owlv2Processor.from_pretrained(MODEL_ID)
    model = Owlv2ForObjectDetection.from_pretrained(MODEL_ID)
    texts = [["human face", "rocket", "nasa badge", "star-spangled banner"]]
    inputs = processor(text=texts, images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_grounded_object_detection(
        outputs=outputs, target_sizes=target_sizes, threshold=0.1, text_labels=texts
    )
    detections = []
    for box, score, label in zip(
        results[0]["boxes"], results[0]["scores"], results[0]["text_labels"]
    ):
        detections.append(
            {
                "label": label,
                "score": round(score.item(), 4),
                "box_xyxy": [round(value, 2) for value in box.tolist()],
            }
        )

    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)
    font = ImageFont.load_default()
    for detection in detections:
        if detection["score"] < VISUAL_THRESHOLD:
            continue
        x1, y1, x2, y2 = detection["box_xyxy"]
        x1 = max(0, min(image.width - 1, int(x1)))
        y1 = max(0, min(image.height - 1, int(y1)))
        x2 = max(0, min(image.width - 1, int(x2)))
        y2 = max(0, min(image.height - 1, int(y2)))
        caption = f'{detection["label"]}: {detection["score"]:.2f}'
        draw.rectangle((x1, y1, x2, y2), outline="#ff2d2d", width=3)
        text_box = draw.textbbox((x1, y1), caption, font=font)
        draw.rectangle(text_box, fill="#ff2d2d")
        draw.text((x1, y1), caption, fill="white", font=font)

    payload = {
        "model": MODEL_ID,
        "image_url": IMAGE_URL,
        "image_size": {"width": image.width, "height": image.height},
        "threshold": 0.1,
        "detections": detections,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    annotated.save(ANNOTATED_OUTPUT)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print(f"Saved results to: {OUTPUT}")
    print(f"Saved annotated image to: {ANNOTATED_OUTPUT}")


if __name__ == "__main__":
    main()
