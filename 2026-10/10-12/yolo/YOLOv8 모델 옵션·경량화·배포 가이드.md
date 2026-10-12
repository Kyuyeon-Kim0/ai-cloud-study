# YOLOv8 모델 옵션·시각화·경량화·배포 가이드

> 기준: Ultralytics YOLOv8. 옵션은 설치된 `ultralytics` 버전 및 작업 유형(detect/segment/pose 등)에 따라 달라질 수 있다. 아래는 **객체 탐지(detect)** 중심의 실무 옵션 정리다.

## 1. 모델 개발 전에 최종 서비스 환경부터 설계

| 대상 환경 | 주요 제약 | 권장 출발점 | 배포 형식 예시 |
|---|---|---|---|
| PC/서버 CPU | 지연시간, 메모리 | YOLOv8n/s | ONNX + ONNX Runtime, OpenVINO |
| NVIDIA GPU 서버 | 처리량, 지연시간 | YOLOv8n~m | TensorRT engine, ONNX |
| 모바일 Android | 전력, 발열, 런타임 지원 | YOLOv8n | TFLite, NCNN (기기별 검증) |
| 모바일 iOS | 메모리, Neural Engine | YOLOv8n | Core ML |
| 일반 USB/IP 비전 카메라 | 카메라는 영상만 전달할 수 있음 | 추론 PC의 사양 기준 | PC에서 ONNX/TensorRT 등 |
| AI 스마트 카메라 | 내장 NPU·제조사 SDK | YOLOv8n 또는 전용 모델 | 제조사 전용 컴파일 모델 |
| 임베디드 Linux | RAM, 전력, 가속기 | YOLOv8n + 양자화 | NCNN, TFLite, ONNX, 전용 형식 |
| MCU급 초저사양 | 극소 RAM·플래시 | YOLOv8도 과할 수 있음 | TFLite Micro 지원 모델 등 별도 설계 |

**개발 흐름:** 대상 하드웨어·FPS·전력·RAM·정확도 요구 정의 → 모델/입력 해상도 선정 → 학습 → 검증 → 변환/양자화 → 실제 장치 벤치마크 → 배포. 변환 뒤에도 전처리, 후처리(NMS), 클래스 매핑, 정확도를 재검증한다.

## 2. 모델 생성 및 학습

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # 사전학습 가중치: n/s/m/l/x
# model = YOLO("yolov8n.yaml")  # 구조부터 생성(가중치 없이 시작)

model.train(
    data="data.yaml", epochs=50, imgsz=640, batch=16,
    device=0, workers=4, patience=15,
    optimizer="auto", project="runs/train", name="exp1"
)
```

### 2.1 학습(train) 옵션 총정리 (주요 공통 설정)

| 옵션 | 의미 | 예시/주의 |
|---|---|---|
| `model` | CLI에서 사용할 모델 | `yolov8n.pt` |
| `data` | 데이터셋 YAML | `data.yaml` |
| `epochs` | 최대 학습 에폭 | `100` |
| `time` | 학습 시간 제한(시간) | 지정 시 epochs보다 우선할 수 있음 |
| `patience` | 조기 종료 대기 에폭 | `30` |
| `batch` | 배치 크기 | `16`, `-1`(자동) |
| `imgsz` | 학습 이미지 크기 | `640` |
| `device` | CPU/GPU/MPS | `"cpu"`, `0`, `"mps"` |
| `workers` | 데이터 로더 워커 수 | Windows에서 문제 시 `0` |
| `cache` | 이미지 캐시 | `False`, `"ram"`, `"disk"` |
| `project`, `name` | 결과 폴더/실험명 | `runs/train`, `exp1` |
| `exist_ok` | 기존 폴더 재사용 | `True` |
| `pretrained` | 사전학습 가중치 사용 | `True` |
| `resume` | 이전 학습 재개 | `True`(체크포인트 필요) |
| `seed`, `deterministic` | 재현성 설정 | `0`, `True` |
| `single_cls` | 모든 클래스를 하나로 취급 | `False` |
| `classes` | 특정 클래스만 학습 | `[0, 2]` (지원 버전 확인) |
| `rect` | 직사각형 배치 | `False` |
| `multi_scale` | 다양한 입력 크기 학습 | 버전별 값 형식 확인 |
| `close_mosaic` | 마지막 N 에폭 모자이크 중단 | `10` |
| `amp` | 혼합정밀도 학습 | `True` |
| `fraction` | 데이터 일부 사용 | `1.0` |
| `freeze` | 일부 레이어 고정 | `10` 또는 레이어 목록 |
| `optimizer` | 최적화 방식 | `auto`, `SGD`, `AdamW` |
| `lr0`, `lrf` | 초기/최종 학습률 비율 | `0.01`, `0.01` |
| `momentum`, `weight_decay` | 최적화 하이퍼파라미터 | `0.937`, `0.0005` |
| `warmup_epochs`, `warmup_momentum`, `warmup_bias_lr` | 워밍업 | `3.0`, `0.8`, `0.1` |
| `cos_lr` | 코사인 학습률 스케줄 | `False` |
| `nbs` | 정규화 기준 배치 | `64` |
| `box`, `cls`, `dfl` | 손실 가중치 | `7.5`, `0.5`, `1.5` (버전별 기본값 확인) |
| `hsv_h`, `hsv_s`, `hsv_v` | 색상 증강 | `0.015`, `0.7`, `0.4` |
| `degrees`, `translate`, `scale`, `shear`, `perspective` | 기하 증강 | `0`, `0.1`, `0.5`, `0`, `0` |
| `flipud`, `fliplr` | 상하/좌우 반전 확률 | `0.0`, `0.5` |
| `mosaic`, `mixup`, `copy_paste` | 합성 증강 | `1.0`, `0.0`, `0.0` (copy_paste는 주로 세그멘테이션) |
| `val`, `plots`, `save`, `save_period` | 검증/그래프/체크포인트 저장 | `True`, `True`, `True`, `-1` |
| `verbose` | 로그 출력 | `True` |

> 모든 설정의 **정확한 최신 목록과 기본값**은 설치 버전의 `ultralytics/cfg/default.yaml` 및 [Ultralytics 설정 문서](https://docs.ultralytics.com/usage/cfg/)를 확인한다. 작업 유형·버전에 따라 `dropout`, `auto_augment`, `erasing`, `pose`, `kobj`, `overlap_mask`, `mask_ratio` 등의 추가 설정이 있다.

## 3. 예측(predict): 신뢰도, 박스 이미지, 좌표, 크롭 저장

```python
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.predict(
    source="test.jpg", conf=0.50, iou=0.45, imgsz=640,
    save=True,       # 박스가 그려진 원본 이미지 저장
    save_txt=True,   # 클래스 ID와 정규화된 박스 좌표 저장
    save_conf=True,  # TXT에 신뢰도 추가(save_txt와 함께)
    save_crop=True,  # 객체 박스 영역만 별도 이미지 저장
    line_width=2,    # 박스 두께
    show=False, max_det=100,
    project="runs/detect", name="demo", exist_ok=True
)
```

### 3.1 예측 옵션 표

| 옵션 | 설명 |
|---|---|
| `source` | 이미지/폴더/영상/웹캠(0)/스트림 |
| `conf` | 최소 신뢰도 임계값(예: `0.5` = 50% 이상) |
| `iou` | NMS에서 중복 박스 제거 IoU 임계값 |
| `imgsz` | 추론 입력 크기 |
| `device` | CPU/GPU 선택 |
| `half` | FP16 추론(지원 하드웨어에서) |
| `batch` | 배치 크기(소스 유형에 따라 적용) |
| `max_det` | 이미지당 최대 탐지 수 |
| `classes` | 특정 클래스만 탐지(예: `[0]` 사람) |
| `agnostic_nms` | 클래스 구분 없이 NMS 수행 |
| `augment` | 테스트 시 증강(TTA) |
| `visualize` | 모델 특성 시각화 |
| `retina_masks` | 고해상도 세그멘테이션 마스크(세그멘테이션용) |
| `stream` | 영상·스트림 결과를 제너레이터로 반환 |
| `stream_buffer` | 실시간 프레임 버퍼링 |
| `vid_stride` | 영상 프레임 간격 |
| `save` | 박스가 그려진 결과 저장 |
| `save_txt` | 라벨과 정규화된 좌표 TXT 저장 |
| `save_conf` | TXT에 신뢰도 저장(단독으로 좌표 TXT 생성하지 않음) |
| `save_crop` | 객체 영역만 크롭 저장 |
| `show` | 창에 결과 표시 |
| `show_labels`, `show_conf`, `show_boxes` | 자동 저장·표시 이미지에서 라벨/신뢰도/박스 표시 여부(버전별 확인) |
| `line_width` | 자동 결과 이미지 박스 선 두께 |
| `project`, `name`, `exist_ok` | 결과 저장 경로 제어 |
| `verbose` | 로그 표시 |
| `rect` | 최소 패딩 기반 추론 |
| `compile` | 지원 환경에서 PyTorch 컴파일(버전 확인) |

결과 예: `runs/detect/demo/test.jpg`, `labels/test.txt`, `crops/person/...jpg`. 파일명과 경로는 버전·입력에 따라 달라진다.

## 4. result[0].plot() 옵션 정리

```python
annotated = results[0].plot(
    conf=True, labels=True, boxes=True,
    line_width=2, font_size=20,
    color_mode="class"
)
```

| 인수 | 기능 | 비고 |
|---|---|---|
| `conf` | 라벨에 신뢰도 수치 표시 | `True/False` |
| `labels` | 클래스 이름/라벨 표시 | `True/False` |
| `boxes` | 바운딩 박스 표시 | `True/False` |
| `line_width` | 박스 선 두께 | 픽셀 단위 정수, `None`은 자동 |
| `font_size` | 라벨 글자 크기 | 주로 픽셀 단위, 렌더링 백엔드 영향 |
| `pil` | PIL 이미지 렌더링 사용 여부 | `True/False`, 일부 기능·문자 처리 시 유용 |
| `img` | 그릴 배경 이미지 지정 | NumPy/PIL 이미지 |
| `kpt_radius` | 포즈 키포인트 반지름 | pose 전용 |
| `kpt_line` | 포즈 키포인트 연결선 | pose 전용 |
| `masks` | 세그멘테이션 마스크 표시 | segment 전용 |
| `probs` | 분류 확률 표시 | classify 전용 |
| `show` | 렌더링된 이미지 표시 | 지원 버전 확인 |
| `save` | plot 결과 파일 저장 | 지원 버전 확인 |
| `filename` | plot 저장 파일명 | `save=True`와 함께 |
| `color_mode` | 클래스별/객체별 색상 모드 | `"class"` / `"instance"` |
| `im_gpu` | 마스크 처리용 GPU 텐서 | 고급 옵션 |
| `txt_color` | 라벨 글자색 | **일반적인 `Results.plot()` 인수에는 없음**. 직접 OpenCV/PIL로 작성 |

**중요:** `plot()`의 인수는 Ultralytics 버전에 따라 변동될 수 있다. 설치된 버전의 실제 인수 확인:

```python
import inspect
from ultralytics.engine.results import Results
print(inspect.signature(Results.plot))
```

`model.predict(conf=0.5)`의 `conf`는 **탐지 필터 기준**, `result.plot(conf=True)`의 `conf`는 **신뢰도 글자 표시 여부**이다.

## 5. conf 글자 크기·색상 조정

### 5.1 글자 크기만 변경

```python
import cv2
image = results[0].plot(font_size=24, line_width=3, conf=True, labels=True)
cv2.imwrite("annotated.jpg", image)
```

### 5.2 글자색을 바꾸거나 conf만 다른 크기로 그리기

`plot()`에는 클래스명과 conf의 글자색·크기를 **각각 따로** 설정하는 표준 인수가 없다. 자동 라벨을 끄고 OpenCV로 직접 그린다. OpenCV 색상은 **BGR** 순서다.

```python
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
result = model("test.jpg", conf=0.5)[0]
image = result.orig_img.copy()
H, W = image.shape[:2]

for box in result.boxes:
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(W, x2), min(H, y2)
    cls = int(box.cls[0])
    score = float(box.conf[0])
    label = result.names[cls]

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    y_text = max(20, y1 - 8)
    cv2.putText(image, label, (x1, y_text),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    # conf만 별도 글자 크기/색상: 노랑(BGR 0,255,255)
    cv2.putText(image, f"{score:.2f}", (x1, min(H - 5, y1 + 24)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

cv2.imwrite("custom_labels.jpg", image)
```

> OpenCV 기본 폰트는 한글 출력이 제한적이다. 한글 라벨은 Pillow의 한글 지원 폰트를 이용한다.

## 6. 박스 좌표 얻기·저장하기

```python
import json
from ultralytics import YOLO

result = YOLO("yolov8n.pt")("test.jpg", conf=0.5)[0]
records = []
for box in result.boxes:
    x1, y1, x2, y2 = box.xyxy[0].tolist()  # 원본 이미지 픽셀 좌표
    cx, cy, w, h = box.xywh[0].tolist()   # 중심 좌표 + 폭/높이 (픽셀)
    cxn, cyn, wn, hn = box.xywhn[0].tolist()  # 0~1 정규화 좌표
    cls_id = int(box.cls[0])
    records.append({
        "class_id": cls_id, "class_name": result.names[cls_id],
        "confidence": float(box.conf[0]),
        "xyxy": [x1, y1, x2, y2],
        "xywh": [cx, cy, w, h],
        "xywhn": [cxn, cyn, wn, hn],
    })

with open("boxes.json", "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
```

| 속성 | 좌표 형식 | 단위 |
|---|---|---|
| `box.xyxy` | 왼쪽 위 `(x1,y1)` + 오른쪽 아래 `(x2,y2)` | 픽셀 |
| `box.xywh` | 중심 `(x,y)` + `(width,height)` | 픽셀 |
| `box.xyxyn` | 정규화된 양 끝 좌표 | 0~1 |
| `box.xywhn` | 정규화된 중심·크기 | 0~1 |
| `box.conf` | 신뢰도 | 0~1 |
| `box.cls` | 클래스 번호 | 정수 |
| `result.names` | 클래스 번호→이름 | 딕셔너리 |

`save_txt=True`의 탐지 라벨은 일반적으로 `class_id cx cy w h [confidence]` 형식이며 좌표는 정규화되어 있다. `save_conf=True`일 때 confidence가 붙는다.

## 7. 객체 박스 영역만 잘라서 저장

**자동:** `model.predict(source="test.jpg", save_crop=True)`.

**직접 저장:**

```python
from pathlib import Path
import cv2
from ultralytics import YOLO

result = YOLO("yolov8n.pt")("test.jpg", conf=0.5)[0]
image = result.orig_img
H, W = image.shape[:2]
Path("crops_custom").mkdir(exist_ok=True)

for i, box in enumerate(result.boxes):
    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(W, x2), min(H, y2)
    if x2 <= x1 or y2 <= y1:
        continue
    crop = image[y1:y2, x1:x2]
    cv2.imwrite(f"crops_custom/object_{i:03d}.jpg", crop)
```

## 8. 경량화 및 최종 서비스 변환

| 방법 | 목적 | 주의 |
|---|---|---|
| YOLOv8n 선택 | 파라미터/연산 감소 | 정확도와 속도 트레이드오프 |
| `imgsz=320` | 추론 연산량 감소 | 모델 파일 용량은 그대로, 작은 객체 정확도 저하 가능 |
| FP16 | 메모리·연산 최적화 | CPU에서 효과 없거나 미지원 가능 |
| INT8 양자화 | 메모리·속도 최적화 | 대표 데이터로 캘리브레이션 필요, 정확도 확인 |
| 구조적 Pruning | 채널·연산 축소 | 실제 속도 향상은 구조·런타임에 좌우, 재학습 필요 가능 |
| Knowledge Distillation | 작은 모델의 성능 개선 | 교사/학생 모델 별도 학습 설계 |
| ONNX | 범용 런타임 호환 | 변환 자체가 곧 경량화는 아님 |
| TensorRT | NVIDIA GPU 최적화 | 호환 GPU/드라이버/런타임 필요 |
| Core ML / TFLite / NCNN | 모바일·엣지 배포 | 연산자 지원, NMS, 입출력 형식 검증 |

```python
from ultralytics import YOLO
model = YOLO("best.pt")

# 필요한 환경에 맞게 하나씩 실행
model.export(format="onnx", imgsz=640, simplify=True)
# model.export(format="engine", imgsz=640, half=True, device=0)  # NVIDIA GPU
# model.export(format="engine", imgsz=640, int8=True, data="data.yaml", device=0)
# model.export(format="tflite", imgsz=640, int8=True, data="data.yaml")
# model.export(format="coreml", imgsz=640)
# model.export(format="ncnn", imgsz=640)
```

`best.pt`는 일반적으로 학습 결과의 `weights/best.pt`에 있다. `format="engine"`은 TensorRT 환경이 필요하다. 지원되지 않는 변환 조합은 오류가 날 수 있다.

### 권장 실험 순서

1. 기준 모델의 mAP50-95, FPS, p95 지연시간, RAM/VRAM, 파일 크기를 측정한다.
2. `yolov8n.pt` 또는 `best.pt` + 입력 크기 640/416/320을 비교한다.
3. 배포 장치가 지원하면 FP16, INT8을 순차 비교한다.
4. 변환 모델의 박스 좌표·클래스·신뢰도·NMS가 원본과 일치하는지 검증한다.
5. 목표 FPS와 정확도를 동시에 만족하는 구성을 채택한다.

## 9. 실습용 통합 예제

```python
from pathlib import Path
import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
results = model.predict(
    "test.jpg", conf=0.5, iou=0.45,
    save=True, save_txt=True, save_conf=True, save_crop=True,
    project="runs/detect", name="all_options", exist_ok=True
)

for result in results:
    print(f"검출 객체 수: {len(result.boxes)}")
    for box in result.boxes:
        print(result.names[int(box.cls[0])], float(box.conf[0]), box.xyxy[0].tolist())
    image = result.plot(line_width=3, font_size=22, conf=True, labels=True)
    cv2.imwrite("result_custom_font.jpg", image)
```

## 10. 공식 참고 문서

- [Ultralytics 설정 전체 목록](https://docs.ultralytics.com/usage/cfg/)
- [Predict 모드](https://docs.ultralytics.com/modes/predict/)
- [Train 모드](https://docs.ultralytics.com/modes/train/)
- [Export 모드](https://docs.ultralytics.com/modes/export/)
- [Results API](https://docs.ultralytics.com/reference/engine/results/)

> 정리: `predict(conf=...)`는 탐지 기준, `plot(conf=...)`는 신뢰도 글자 표시 여부, `plot(font_size=...)`는 라벨 크기, 글자색/클래스명과 conf의 개별 스타일은 OpenCV/PIL 직접 그리기로 처리한다.
