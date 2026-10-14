"""웹캠 영상에서 사람을 분할하고 배경을 교체하는 PyTorch 프로그램.

사용 방법:
1. back2.jpg를 이 파일과 같은 폴더에 둡니다.
2. 필요한 패키지를 설치합니다: pip install torch torchvision opencv-python pillow numpy
3. 실행합니다: python main.py
4. 종료하려면 q 키를 누릅니다.
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
    # GPU가 있으면 사용하고, 없으면 CPU로 실행합니다.
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"사용 장치: {device}")

    # 사전 학습된 DeepLabV3 모델을 불러와 추론 모드로 설정합니다.
    weights = DeepLabV3_ResNet50_Weights.DEFAULT
    model = deeplabv3_resnet50(weights=weights).to(device).eval()
    preprocess = weights.transforms()

    # 이 스크립트와 같은 폴더에 있는 배경 이미지를 불러옵니다.
    background_path = Path(__file__).resolve().parent / "back.jpg"
    background = cv2.imread(str(background_path))
    if background is None:
        raise FileNotFoundError(f"배경 이미지를 찾을 수 없습니다: {background_path}")

    # 기본 웹캠(장치 번호 0)에 연결합니다.
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.release()
        raise RuntimeError("웹캠을 열 수 없습니다. 연결 및 권한을 확인하세요.")

    try:
        # 웹캠 프레임을 읽어 사람 분할과 배경 합성을 반복합니다.
        while True:
            ret, frame = cap.read()
            if not ret:
                print("웹캠 프레임을 읽지 못했습니다.")
                break

            height, width = frame.shape[:2]
            resized_background = cv2.resize(background, (width, height))

            # OpenCV의 BGR 프레임을 모델 입력용 RGB 이미지로 변환합니다.
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            input_tensor = preprocess(Image.fromarray(rgb))
            input_batch = input_tensor.unsqueeze(0).to(device)

            # 각 픽셀의 클래스를 예측합니다. VOC의 사람 클래스 인덱스는 15입니다.
            with torch.inference_mode():
                output = model(input_batch)["out"]
            prediction = output.argmax(dim=1)[0]
            person_mask = (prediction == 15).to(torch.uint8).cpu().numpy()

            # 사람 마스크를 원본 프레임 크기로 되돌립니다.
            person_mask = cv2.resize(
                person_mask, (width, height), interpolation=cv2.INTER_NEAREST
            )

            # 사람 영역은 원본 프레임으로, 나머지는 배경 이미지로 채웁니다.
            mask_3ch = person_mask[:, :, None]
            result = np.where(mask_3ch.astype(bool), frame, resized_background)

            # 원본 영상과 배경 합성 결과를 화면에 표시합니다.
            cv2.imshow("원본 영상", frame)
            cv2.imshow("사람 분할 및 배경 교체", result)

            # q 키를 누르면 프로그램을 종료합니다.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        # 오류가 발생하거나 종료할 때 웹캠과 창을 정리합니다.
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
