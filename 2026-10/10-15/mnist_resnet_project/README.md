# MNIST ResNet18 전이학습 프로젝트

ImageNet으로 사전 학습된 ResNet18을 MNIST 숫자 분류에 맞게 전이학습하고, 테스트 성능과 예측 결과를 분석하는 실습입니다.

## 주요 내용

- MNIST 샘플 이미지와 ResNet18 특징 맵 시각화
- 특징 맵 통계를 활용한 레이어 동결·학습 범위 제안
- 일부 MNIST 학습 데이터로 CPU 빠른 학습 실험
- 테스트셋 분류 보고서, 혼동 행렬, 오분류 이미지, Grad-CAM 생성

## 실행 환경

- Python 3
- PyTorch 및 torchvision
- matplotlib, NumPy, pandas, scikit-learn, tqdm, Pillow
- `03_gpt_analysis.py`를 실행할 경우 `openai` 패키지와 OpenAI API 키

PyTorch와 torchvision은 사용하는 CPU 또는 CUDA 환경에 맞게 설치하세요. 나머지 패키지는 다음처럼 설치할 수 있습니다.

```powershell
pip install matplotlib numpy pandas scikit-learn tqdm pillow openai
```

## 실행 방법

PowerShell에서 이 폴더로 이동합니다.

```powershell
cd C:\ai-starter\2026-10\10-15\mnist_resnet_project
```

실습을 처음부터 실행하려면 다음 순서를 따릅니다.

```powershell
python 01_mnist_sample.py
python 02_feature_map.py
python 03_gpt_analysis.py
python 04_train.py
python 05_evaluate.py
```

`03_gpt_analysis.py`는 `outputs/feature_maps.png`와 `outputs/feature_stats.json`을 분석하고 `outputs/freeze_analysis.json`을 만듭니다. OpenAI API를 사용하므로 `.env`에 `OPENAI_API_KEY`를 설정해야 하며 API 사용료가 발생할 수 있습니다. 분석 파일이 이미 있으면 이 단계는 건너뛰고 학습을 실행할 수 있습니다.

`04_train.py`는 MNIST 학습 데이터 중 5,000장과 검증 데이터 1,000장을 사용해 CPU에서 3 epoch 학습합니다. 첫 실행 시 MNIST와 ImageNet 사전 학습 가중치를 내려받을 수 있습니다. 학습 후 `05_evaluate.py`가 별도 테스트 이미지 10,000장으로 평가합니다. 평가 코드는 진행률을 표시하며, 학습과 같은 112×112 입력 크기를 사용합니다.

## 결과

한 번의 평가 실행에서 테스트 정확도는 **98.78% (9,878/10,000)**였습니다. 학습 설정이나 실행 환경에 따라 결과는 달라질 수 있습니다.

평가 결과와 시각화 파일은 `outputs/`에 저장됩니다.

| 파일 | 설명 |
|---|---|
| `classification_report.csv` | 숫자별 정밀도, 재현율, F1 점수 |
| `evaluation.json` | 정확도, 혼동 행렬, 분류 보고서 및 학습 설정 |
| `confusion_matrix.png` | 테스트셋 혼동 행렬 |
| `misclassified.png` | 오분류된 숫자 예시 |
| `gradcam.png` | 선택된 테스트 이미지의 Grad-CAM 시각화 |
| `training_history_cpu_fast.json` | epoch별 학습·검증 기록 |
| `feature_maps.png`, `feature_stats.json` | 중간 특징 맵과 통계 |
| `freeze_analysis.json` | GPT가 제안한 레이어 동결·학습 설정 |

## 파일 구성

| 파일 | 설명 |
|---|---|
| `01_mnist_sample.py` | MNIST 샘플 이미지 저장 |
| `02_feature_map.py` | 사전 학습 ResNet18 특징 맵 추출 및 통계 저장 |
| `03_gpt_analysis.py` | 특징 맵 분석 및 레이어 학습 설정 제안 |
| `04_train.py` | ResNet18 MNIST 전이학습 |
| `05_evaluate.py` | 테스트 평가와 시각화 결과 저장 |

MNIST 데이터는 `data/`에 내려받고, 모델 체크포인트는 `outputs/best_model_cpu_fast.pth`에 저장합니다. 두 항목은 프로젝트 `.gitignore`에서 제외되어 있습니다. 결과 보고서와 그림 파일은 Git에 포함할 수 있습니다.
