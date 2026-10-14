# 이진 분류 학습 예제

세 가지 스크립트로 로지스틱 회귀와 PyTorch 신경망의 이진 분류 학습 과정을 살펴봅니다. 예제 데이터는 코드 안에서 생성하는 작은 인공 데이터이며, 실제 문제에 학습된 모델은 아닙니다.

## 파일 구성

```text
binary_classification/
├── lr_test.py           # 직접 구현한 로지스틱 회귀와 학습률 비교
├── torch_binary.py      # PyTorch 미니배치 학습과 가중치 변화 확인
├── pytorch_binary.py    # 데이터 분할, 정규화, 조기 종료 및 평가
├── best_model.pt        # pytorch_binary.py의 저장 체크포인트
└── training_history.png # 학습 및 검증 손실 그래프
```

## 설치

PowerShell에서 이 폴더로 이동한 뒤 필요한 패키지를 설치합니다.

```powershell
python -m pip install torch matplotlib
```

## 실행

각 예제를 폴더 안에서 실행합니다.

```powershell
python lr_test.py
python torch_binary.py
python pytorch_binary.py
```

### 스크립트별 내용

- `lr_test.py`: 로지스틱 회귀의 가중치와 편향을 직접 갱신하며 학습률 `0.001`, `0.1`, `1`, `10`에 따른 손실 변화를 비교합니다. 추가 패키지는 필요하지 않습니다.
- `torch_binary.py`: PyTorch 신경망을 미니배치로 2 epoch 학습하고, 학습 전후 파라미터와 예측 결과를 출력합니다.
- `pytorch_binary.py`: 학습·검증·테스트 데이터 분할, 입력 정규화, 검증 손실 기준 조기 종료를 적용합니다. 최적 가중치를 `best_model.pt`에 저장하고 손실 그래프를 `training_history.png`로 만듭니다.

`pytorch_binary.py` 실행 시 체크포인트와 그래프 파일이 같은 폴더에 생성되거나 갱신됩니다. 이 예제들은 학습 절차를 익히기 위한 장난감 데이터이므로, 정확도 수치를 실제 데이터 성능으로 해석하지 마세요.
