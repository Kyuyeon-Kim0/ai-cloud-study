# 2026-10-15 (목) 학습 기록

## 학습 주제

- 사전 학습된 ResNet18의 특징 맵 시각화
- GPT 분석을 참고한 전이학습 레이어 동결 범위 설정
- ResNet18을 이용한 MNIST 숫자 분류와 테스트 결과 분석

## 실습 내용

### ResNet18 특징 맵 관찰

ImageNet 사전 학습 ResNet18에 이미지를 입력하고 `conv1`, `layer1`부터 `layer4`까지의 특징 맵을 확인했습니다. MNIST 샘플로 중간 특징을 시각화하고, 통계를 바탕으로 동결할 레이어와 학습할 레이어를 제안받았습니다. 이 제안은 실험을 위한 출발점이며, 최적 설정은 검증 데이터로 비교해야 합니다.

### MNIST 전이학습

ImageNet 가중치를 불러온 ResNet18의 마지막 분류층을 숫자 10개에 맞게 교체했습니다. CPU에서 MNIST 학습 데이터 5,000장과 검증 데이터 1,000장을 사용해 3 epoch 동안 빠르게 학습했습니다. 모델 입력은 회색조 이미지를 3채널로 바꾸고 112×112 크기로 조정했습니다.

테스트에서는 별도로 분리된 MNIST 테스트 이미지 10,000장을 평가했습니다. 학습과 평가의 입력 크기를 동일하게 맞춘 실행에서 정확도는 **98.78% (9,878/10,000)**였습니다. 정확도는 실행 환경과 학습 결과에 따라 달라질 수 있습니다.

## 실행 방법

PowerShell에서 프로젝트 폴더로 이동한 뒤 순서대로 실행합니다.

```powershell
cd C:\ai-starter\2026-10\10-15\mnist_resnet_project
python 01_mnist_sample.py
python 02_feature_map.py
python 03_gpt_analysis.py
python 04_train.py
python 05_evaluate.py
```

`03_gpt_analysis.py`는 OpenAI API를 사용하므로 `.env`에 `OPENAI_API_KEY`가 필요하며 API 사용료가 발생할 수 있습니다. 이미 생성된 `outputs/freeze_analysis.json`을 사용할 경우 해당 분석 스크립트 실행을 건너뛰고 학습을 진행할 수 있습니다. 첫 실행에서는 MNIST 데이터와 ImageNet 사전 학습 가중치를 내려받을 수 있습니다.

## 주요 파일

| 파일 | 설명 |
|---|---|
| [전이학습_test.py](전이학습_test.py) | 입력 이미지에 대한 ResNet18 특징 맵과 ImageNet 예측 상위 5개 확인 |
| [gpt_resnet_freeze.py](gpt_resnet_freeze.py) | 특징 맵 분석 결과를 OpenAI API로 보내 동결·학습 레이어 제안 및 JSON 저장 |
| [mnist_resnet_project/](mnist_resnet_project/) | MNIST 샘플, 특징 맵 분석, 학습 및 평가 코드 |
| [gpt_analysis.json](gpt_analysis.json) | 별도 ResNet18 특징 분석 실습에서 저장한 레이어 제안 |
| [resnet18_features.png](resnet18_features.png) | 쿼카 이미지의 ResNet18 레이어별 특징 요약 시각화 |
| [feature_maps.png](feature_maps.png) | 쿼카 이미지에서 ResNet18의 conv1·layer1~layer4별 활성도가 높은 채널 4개를 골라 시각화한 결과 |
| [mnist_resnet_project/outputs/classification_report.csv](mnist_resnet_project/outputs/classification_report.csv) | MNIST 클래스별 정밀도·재현율·F1 보고서 |
| [mnist_resnet_project/outputs/confusion_matrix.png](mnist_resnet_project/outputs/confusion_matrix.png) | 테스트 혼동 행렬 |
| [mnist_resnet_project/outputs/misclassified.png](mnist_resnet_project/outputs/misclassified.png) | 오분류 예시 |
| [mnist_resnet_project/outputs/gradcam.png](mnist_resnet_project/outputs/gradcam.png) | 예측에 대한 Grad-CAM 시각화 |

학습 데이터와 모델 체크포인트는 저장소에 포함하지 않습니다. 데이터는 실행 시 내려받으며, 결과 파일은 `mnist_resnet_project/outputs/`에 저장됩니다.
