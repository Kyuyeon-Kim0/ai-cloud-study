from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np


# MediaPipe Face Mesh에서 양쪽 눈의 바깥/안쪽 끝점
EYES = ((33, 133), (362, 263))


def load_overlay(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"이미지를 읽을 수 없습니다: {path}")

    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
    elif image.shape[2] == 3:
        # 첨부 이미지처럼 흰 배경인 경우 밝기에 따라 부드러운 투명도를 생성한다.
        bgr = image
        alpha = np.clip(255 - (bgr.min(axis=2).astype(np.int16) - 235) * 13, 0, 255)
        image = np.dstack((bgr, alpha.astype(np.uint8)))
    return image


def rotate_rgba(image: np.ndarray, angle: float) -> np.ndarray:
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    cos, sin = abs(matrix[0, 0]), abs(matrix[0, 1])
    new_w, new_h = int(h * sin + w * cos), int(h * cos + w * sin)
    matrix[0, 2] += new_w / 2 - w / 2
    matrix[1, 2] += new_h / 2 - h / 2
    return cv2.warpAffine(
        image, matrix, (new_w, new_h), flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0)
    )


def alpha_blend(frame: np.ndarray, overlay: np.ndarray, center: tuple[int, int]) -> None:
    oh, ow = overlay.shape[:2]
    x1, y1 = center[0] - ow // 2, center[1] - oh // 2
    x2, y2 = x1 + ow, y1 + oh
    fx1, fy1, fx2, fy2 = max(0, x1), max(0, y1), min(frame.shape[1], x2), min(frame.shape[0], y2)
    if fx1 >= fx2 or fy1 >= fy2:
        return

    crop = overlay[fy1 - y1:fy2 - y1, fx1 - x1:fx2 - x1]
    alpha = crop[:, :, 3:4].astype(np.float32) / 255.0
    frame[fy1:fy2, fx1:fx2] = (
        crop[:, :, :3] * alpha + frame[fy1:fy2, fx1:fx2] * (1.0 - alpha)
    ).astype(np.uint8)


def run(image_path: Path, camera: int, scale: float) -> int:
    try:
        fire = load_overlay(image_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[오류] {exc}", file=sys.stderr)
        return 1

    cap = cv2.VideoCapture(camera)
    if not cap.isOpened():
        print(f"[오류] 웹캠 {camera}을(를) 열 수 없습니다.", file=sys.stderr)
        return 1

    face_mesh = mp.solutions.face_mesh.FaceMesh(
        max_num_faces=1, refine_landmarks=True,
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    )
    print("종료하려면 영상 창에서 Q 또는 ESC를 누르세요.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[오류] 웹캠 영상을 읽지 못했습니다.", file=sys.stderr)
                break

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = face_mesh.process(rgb)

            if result.multi_face_landmarks:
                h, w = frame.shape[:2]
                marks = result.multi_face_landmarks[0].landmark
                for outer_idx, inner_idx in EYES:
                    p1 = np.array([marks[outer_idx].x * w, marks[outer_idx].y * h])
                    p2 = np.array([marks[inner_idx].x * w, marks[inner_idx].y * h])
                    eye_width = max(12, int(np.linalg.norm(p2 - p1)))
                    target_w = max(20, int(eye_width * scale))
                    target_h = max(20, int(target_w * fire.shape[0] / fire.shape[1]))
                    resized = cv2.resize(fire, (target_w, target_h), interpolation=cv2.INTER_AREA)
                    angle = -np.degrees(np.arctan2(p2[1] - p1[1], p2[0] - p1[0]))
                    rotated = rotate_rgba(resized, angle)
                    center = tuple(((p1 + p2) / 2).astype(int))
                    alpha_blend(frame, rotated, center)

            cv2.imshow("MediaPipe Eye Fire", frame)
            if (cv2.waitKey(1) & 0xFF) in (ord("q"), ord("Q"), 27):
                break
    except KeyboardInterrupt:
        pass
    finally:
        face_mesh.close()
        cap.release()
        cv2.destroyAllWindows()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="웹캠의 양쪽 눈에 PNG 이미지를 합성합니다.")
    parser.add_argument("--image", type=Path, default=Path(__file__).with_name("a.png"))
    parser.add_argument("--camera", type=int, default=0, help="웹캠 번호 (기본값: 0)")
    parser.add_argument("--scale", type=float, default=2.2, help="눈 너비 대비 이미지 배율")
    args = parser.parse_args()
    if args.scale <= 0:
        parser.error("--scale은 0보다 커야 합니다.")
    return run(args.image, args.camera, args.scale)


if __name__ == "__main__":
    raise SystemExit(main())
