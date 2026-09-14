"""MediaPipe Face Mesh: 얼굴 연결선과 랜드마크 번호 표시."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import mediapipe as mp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="얼굴에 MediaPipe 랜드마크를 표시합니다.")
    parser.add_argument("--image", type=Path, help="입력 이미지 경로(생략하면 웹캠)")
    parser.add_argument("--camera", type=int, default=0, help="웹캠 번호 (기본값: 0)")
    parser.add_argument("--output", type=Path, default=Path("result.jpg"), help="저장 경로")
    parser.add_argument("--no-numbers", action="store_true", help="랜드마크 번호 숨기기")
    parser.add_argument("--number-step", type=int, default=1, help="N개마다 번호 표시 (기본값: 1)")
    parser.add_argument("--max-faces", type=int, default=1, help="인식할 최대 얼굴 수")
    return parser.parse_args()


def draw_face_mesh(frame, results, show_numbers: bool, number_step: int):
    annotated = frame.copy()
    height, width = annotated.shape[:2]
    drawing = mp.solutions.drawing_utils
    styles = mp.solutions.drawing_styles
    face_mesh = mp.solutions.face_mesh

    if not results.multi_face_landmarks:
        return annotated

    for landmarks in results.multi_face_landmarks:
        drawing.draw_landmarks(
            image=annotated,
            landmark_list=landmarks,
            connections=face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=styles.get_default_face_mesh_tesselation_style(),
        )
        drawing.draw_landmarks(
            image=annotated,
            landmark_list=landmarks,
            connections=face_mesh.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=styles.get_default_face_mesh_contours_style(),
        )

        if show_numbers:
            for index, point in enumerate(landmarks.landmark):
                if index % number_step != 0:
                    continue
                x, y = int(point.x * width), int(point.y * height)
                cv2.circle(annotated, (x, y), 1, (0, 180, 0), -1)
                cv2.putText(
                    annotated,
                    str(index),
                    (x + 2, y - 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.28,
                    (0, 130, 0),
                    1,
                    cv2.LINE_AA,
                )
    return annotated


def make_detector(max_faces: int):
    return mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=max_faces,
        refine_landmarks=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def process_image(args: argparse.Namespace) -> None:
    frame = cv2.imread(str(args.image))
    if frame is None:
        raise SystemExit(f"이미지를 읽을 수 없습니다: {args.image}")

    with make_detector(args.max_faces) as detector:
        results = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        output = draw_face_mesh(frame, results, not args.no_numbers, args.number_step)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), output):
        raise SystemExit(f"결과를 저장할 수 없습니다: {args.output}")
    print(f"저장 완료: {args.output.resolve()}")


def process_camera(args: argparse.Namespace) -> None:
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        raise SystemExit(f"웹캠 {args.camera}번을 열 수 없습니다.")

    last_frame = None
    with make_detector(args.max_faces) as detector:
        try:
            while True:
                ok, frame = camera.read()
                if not ok:
                    print("웹캠 영상을 읽지 못했습니다.")
                    break
                frame = cv2.flip(frame, 1)
                results = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                last_frame = draw_face_mesh(frame, results, not args.no_numbers, args.number_step)
                cv2.imshow("MediaPipe Face Mesh - Q: quit, S: save", last_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("s"):
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(str(args.output), last_frame)
                    print(f"저장 완료: {args.output.resolve()}")
                elif key == ord("q"):
                    break
        finally:
            camera.release()
            cv2.destroyAllWindows()


def main() -> None:
    args = parse_args()
    if args.number_step < 1:
        raise SystemExit("--number-step은 1 이상이어야 합니다.")
    if args.image:
        process_image(args)
    else:
        process_camera(args)


if __name__ == "__main__":
    main()
