from ultralytics import YOLO


# 모델 로드
model = YOLO("yolov8n.pt")

# 동영상 처리 & 저장
#result = model('../sample_video.mp4', save=True)
result = model('./sample_video.mp4', show=True)

print(result)