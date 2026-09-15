import cv2
import numpy as np

cap = cv2.VideoCapture(0)

gray_mode = False
bright_mode = False

start_x, start_y = -1, -1
end_x, end_y = -1, -1
dragging = False

current_frame = None


# 마우스 드래그 함수
def mouse_event(event, x, y, flags, param):
    global start_x, start_y, end_x, end_y
    global dragging, current_frame

    # 마우스 왼쪽 버튼 누름
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
        dragging = True

    # 드래그 중
    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging:
            end_x, end_y = x, y

    # 마우스 버튼 뗌
    elif event == cv2.EVENT_LBUTTONUP:
        end_x, end_y = x, y
        dragging = False

        # 좌표 정리
        x1 = min(start_x, end_x)
        y1 = min(start_y, end_y)
        x2 = max(start_x, end_x)
        y2 = max(start_y, end_y)

        # 선택 영역 저장
        roi = current_frame[y1:y2, x1:x2]

        if roi.size > 0:
            cv2.imwrite("selected_area.jpg", roi)
            print("선택 영역 저장 완료")


cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", mouse_event)


while True:

    ret, frame = cap.read()

    if not ret:
        print("웹캠을 읽을 수 없습니다.")
        break

    # 원본 보관
    current_frame = frame.copy()

    # a : 회색 모드
    if gray_mode:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 사각형 표시를 위해 다시 BGR로 변환
        frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # b : 밝기 증가
    if bright_mode:
        frame = cv2.convertScaleAbs(
            frame,
            alpha=1.0,
            beta=100
        )

    # 드래그 중이면 사각형 표시
    if dragging:
        cv2.rectangle(
            frame,
            (start_x, start_y),
            (end_x, end_y),
            (0, 255, 0),
            2
        )

    cv2.imshow("Webcam", frame)

    key = cv2.waitKey(1) & 0xFF

    # q : 종료
    if key == ord("q"):
        break

    # s : 현재 프레임 저장
    elif key == ord("s"):
        cv2.imwrite("frame.jpg", frame)
        print("현재 프레임 저장 완료")

    # a : 회색 ON/OFF
    elif key == ord("a"):
        gray_mode = not gray_mode
        print("회색 모드:", gray_mode)

    # b : 밝기 ON/OFF
    elif key == ord("b"):
        bright_mode = not bright_mode
        print("밝기 모드:", bright_mode)


cap.release()
cv2.destroyAllWindows()