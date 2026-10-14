# 2026-10-14 (수) 학습 기록

## 학습 주제  

- 이미지 분류와 사전 학습 모델 활용
- 개방형 어휘 객체 탐지
- 웹캠 인물 분할 및 배경 교체
- 이진 분류와 학습률에 따른 학습 비교

## 핵심 이해

### 사전 학습 모델과 이미지 분류

- AlexNet은 ImageNet으로 학습된 가중치를 불러와 이미지의 클래스를 예측할 수 있습니다.
- 모델 입력 크기에 맞춘 전처리와 ImageNet 정규화가 필요합니다.
- 예측 클래스 번호는 ImageNet 클래스 이름 목록과 연결해 확인합니다.

### 객체 탐지와 이미지 분할

- OWLv2는 텍스트로 지정한 대상을 이미지에서 탐지하고 점수와 경계 상자를 반환합니다.
- DeepLabV3는 픽셀마다 클래스를 예측하며, 사람 영역 마스크를 이용해 배경을 합성할 수 있습니다.
- 예측 점수와 분류 결과는 모델의 추정이므로 실제 정답과 다를 수 있습니다.

### 이진 분류 학습

- 시그모이드와 이진 교차 엔트로피 손실을 이용해 두 클래스 중 하나를 예측합니다.
- 학습률은 가중치 갱신 크기에 영향을 주며, 적절하지 않으면 학습이 느리거나 불안정할 수 있습니다.
- 학습·검증·테스트 데이터를 나누고 검증 손실 기준 조기 종료를 적용할 수 있습니다.

## 실습 내용

- AlexNet으로 고양이, 개, 배 이미지 분류
- OWLv2에 텍스트 탐지 대상을 지정하고 JSON 및 표시 이미지를 저장
- 웹캠에서 사람을 분할하고 지정한 배경 이미지로 교체
- 직접 구현한 로지스틱 회귀와 PyTorch 이진 분류 학습 비교

## 실습 파일

| 파일 또는 폴더 | 내용 |
| --- | --- |
| [alexnet_image_classification/](alexnet_image_classification/README.md) | AlexNet 이미지 분류 예제와 실행 안내 |
| [owlv2_object_detection/](owlv2_object_detection/README.md) | OWLv2 텍스트 기반 객체 탐지 |
| [segmentation_dashboard/](segmentation_dashboard/README.md) | 웹캠 인물 분할 대시보드와 히스토그램 분석 |
| [webcam_person_segmentation/](webcam_person_segmentation/README.md) | 웹캠 인물 분할과 배경 교체 |
| [binary_classification/](binary_classification/README.md) | 로지스틱 회귀와 PyTorch 이진 분류 실습 |
| [lr_test.py](lr_test.py) | 학습률에 따른 손실 변화 비교 |

## 실행 방법

각 프로젝트의 세부 설치 및 실행 방법은 해당 폴더의 README를 참고 바랍니다. Python 예제는 프로젝트 폴더에서 실행합니다. 예를 들면:

```powershell
cd C:\ai-starter\2026-10\10-14\binary_classification
python pytorch_binary.py
```

모델 가중치 다운로드, GPU 사용 여부, API 키와 같은 실행 조건은 각 프로젝트 README에 정리되어 있습니다.
