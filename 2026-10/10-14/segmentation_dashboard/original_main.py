"""PyTorch DeepLabV3 webcam person segmentation with background replacement.

Place back.jpg next to this script, install dependencies, then run:
    pip install torch torchvision opencv-python pillow numpy
    python main.py
Press q to quit.
"""
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision.models.segmentation import (
    DeepLabV3_ResNet50_Weights,
    deeplabv3_resnet50,
)


def main() -> None:
    # 1. GPU가 있으면 사용하고, 없으면 CPU로 실행합니다.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"사용 장치: {device}")

    # 2. 사전학습된 DeepLabV3 모델을 불러와 추론 모드로 전환합니다.
    weights = DeepLabV3_ResNet50_Weights.DEFAULT
    model = deeplabv3_resnet50(weights=weights).to(device).eval()
    preprocess = weights.transforms()

    # 3. 이 스크립트와 같은 폴더에서 배경 이미지를 읽습니다.
    background_path = Path(__file__).resolve().parent / "back.jpg"
    background = cv2.imread(str(background_path))
    if background is None:
        raise FileNotFoundError(f"배경 이미지가 없습니다: {background_path}")

    # 4. 기본 웹캠(0번)을 연결합니다.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("웹캠을 열 수 없습니다. 카메라 연결 및 권한을 확인하세요.")

    try:
        # 5. 웹캠에서 프레임을 계속 읽어 처리합니다.
        while True:
            ret, frame = cap.read()
            if not ret:
                print("웹캠 프레임을 읽지 못했습니다.")
                break

            height, width = frame.shape[:2]
            bg = cv2.resize(background, (width, height))

            # 6. OpenCV의 BGR 이미지를 모델 입력용 RGB/PIL 이미지로 바꿉니다.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = preprocess(Image.fromarray(rgb))
            input_batch = input_tensor.unsqueeze(0).to(device)

            # 7. 픽셀별 클래스를 예측합니다. VOC 기준 사람 클래스는 15입니다.
            with torch.inference_mode():
                output = model(input_batch)["out"]
            prediction = output.argmax(dim=1)[0]
            person_mask = (prediction == 15).to(torch.uint8).cpu().numpy()

            # 8. 사람 마스크를 원본 영상 크기로 복원합니다.
            person_mask = cv2.resize(
                person_mask, (width, height), interpolation=cv2.INTER_NEAREST
            )

            # 9. 사람 픽셀은 웹캠 원본, 나머지는 back.jpg로 합성합니다.
            mask_3ch = person_mask[:, :, None]
            result = np.where(mask_3ch.astype(bool), frame, bg)

            # 10. 원본 영상과 합성 결과를 화면에 표시합니다.
            cv2.imshow("Original", frame)
            cv2.imshow("Person Segmentation", result)

            # 11. q 키를 누르면 종료합니다.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        # 12. 오류가 나거나 종료할 때 웹캠과 창을 정리합니다.
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
