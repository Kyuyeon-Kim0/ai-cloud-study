# 2026-10-13 (화) 학습 기록

## 학습 주제

- YOLOv8 Pose를 이용한 사람 자세 및 키포인트 추론
- YOLO 객체 탐지 결과를 이용한 회의실 상태 분석
- YOLO 영상 분석과 GPT 프롬프트를 결합한 보고서 작성
- 제조 공정 영상에서 작업자 동선과 생산성·안전성 분석

## 핵심 이해

### YOLOv8 Pose

- 사전 학습된 Pose 모델로 이미지 속 사람의 키포인트를 추론하고 시각화합니다.
- 탐지 결과의 키포인트 좌표를 이용해 자세나 신체 부위의 위치를 분석할 수 있습니다.

### 객체 탐지와 프롬프트 엔지니어링

- YOLO 탐지 결과에서 객체의 클래스와 개수를 추출해 회의실 상태를 요약할 수 있습니다.
- 구조화한 탐지 결과를 프롬프트에 포함해 GPT가 분석 보고서를 작성하도록 구성합니다.

### 영상 분석

- 영상의 프레임을 추출해 YOLO 추론을 수행하고 시간에 따른 사람의 위치 변화를 기록합니다.
- 분석 결과를 표나 그래프로 정리하면 작업자 동선과 공정 상태를 살펴볼 수 있습니다.

## 실습 내용

- YOLOv8 Pose 모델로 이미지의 사람 키포인트 추론
- 회의실 이미지·영상에서 객체를 탐지하고 상태 정보 집계
- 탐지 결과를 GPT 프롬프트에 전달해 분석 보고서 생성
- 제조 공정 영상에서 사람 위치 변화와 시간별 결과 시각화

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [yolo_test.ipynb](yolo_test.ipynb) | YOLOv8 Pose 모델의 이미지 추론 실습 |
| [yolo활용 & GPT프롬프트.ipynb](yolo%ED%99%9C%EC%9A%A9%20%26%20GPT%ED%94%84%EB%A1%AC%ED%94%84%ED%8A%B8.ipynb) | 회의실 분석, GPT 보고서 생성, 제조 공정 영상 분석 노트북 |
| [yolov8n-pose.pt](yolov8n-pose.pt) | Pose 추론에 사용하는 YOLOv8 모델 파일 |
| [test_pose.jpg](test_pose.jpg) | Pose 추론용 테스트 이미지 |
| [runs/pose/predict/](runs/pose/predict/) | Pose 추론 결과 이미지가 저장된 폴더 |

## 실행 방법

- 노트북을 Jupyter 또는 Google Colab에서 엽니다.
- `yolo_test.ipynb`는 노트북과 같은 폴더에 `yolov8n-pose.pt`와 `test_pose.jpg`가 있는지 확인한 뒤 셀을 순서대로 실행합니다.
- 객체 탐지·GPT 실습은 노트북에 안내된 런타임과 패키지를 준비합니다. GPT API를 사용하는 셀은 본인의 API 키 설정이 필요합니다.
- Before running GPT cells, set the `OPENAI_API_KEY` environment variable; do not hardcode the key in the notebook.
