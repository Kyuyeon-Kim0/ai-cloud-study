import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

# -----------------------------------
# 1. 데이터 준비
# -----------------------------------
X = np.array([
    [1, 10], [2, 20], [3, 30], [4, 40],
    [5, 50], [6, 60], [7, 70], [8, 80],
    [9, 90], [10, 100], [11, 110], [12, 120],
    [13, 130], [14, 140], [15, 150], [16, 160],
    [17, 170], [18, 180], [19, 190], [20, 200]
])

y = np.array([
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1
])

# -----------------------------------
# 2. 데이터 분리
# -----------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# -----------------------------------
# 3. Min-Max 정규화
# -----------------------------------
scaler = MinMaxScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n[정규화 기준]")
print("최솟값:", scaler.data_min_)
print("최댓값:", scaler.data_max_)

print("\n[정규화 전후 비교]")
for i in range(len(X_train)):
    print(X_train[i], "->", X_train_scaled[i].round(3))


# -----------------------------------
# 4. 학습 결과 확인 함수
# -----------------------------------
def show_fit_result(model, X, y):
    print("\n===== FIT 결과 =====")

    print("가중치:", model.coef_)
    print("절편:", model.intercept_)
    print("반복 횟수:", model.n_iter_)

    # 선형 결합값 z = wx + b
    z_values = model.decision_function(X)

    # 시그모이드 통과 후 확률
    probabilities = model.predict_proba(X)[:, 1]

    # 최종 예측
    predictions = model.predict(X)

    print("\n[훈련 데이터별 결과]")
    for i in range(len(X)):
        print(
            f"{i+1:02d} | "
            f"z={z_values[i]:7.3f} | "
            f"확률={probabilities[i]:.3f} | "
            f"예측={predictions[i]} | "
            f"실제={y[i]}"
        )


# -----------------------------------
# 5. 로지스틱 회귀 학습
# -----------------------------------
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

show_fit_result(model, X_train_scaled, y_train)


# -----------------------------------
# 6. 분류 검증 리포트 함수
# -----------------------------------
def show_report(y_true, y_pred, title):
    print(f"\n===== {title} =====")

    print("혼동행렬:")
    print(confusion_matrix(y_true, y_pred))

    print("\n분류 리포트:")
    print(classification_report(
        y_true,
        y_pred,
        target_names=["불합격", "합격"],
        zero_division=0
    ))


# 훈련 데이터 평가
train_pred = model.predict(X_train_scaled)
show_report(y_train, train_pred, "훈련 데이터 평가")

# 테스트 데이터 평가
test_pred = model.predict(X_test_scaled)
show_report(y_test, test_pred, "테스트 데이터 평가")


# -----------------------------------
# 7. 임계값 조정 함수
# -----------------------------------
def predict_threshold(model, X, threshold=0.5):
    probabilities = model.predict_proba(X)[:, 1]

    predictions = (probabilities >= threshold).astype(int)

    return predictions


# -----------------------------------
# 8. 여러 임계값 비교
# -----------------------------------
print("\n===== 임계값 비교 =====")

thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]

for threshold in thresholds:
    pred = predict_threshold(
        model,
        X_train_scaled,
        threshold
    )

    print(
        f"임계값={threshold:.1f} | "
        f"Accuracy={accuracy_score(y_train, pred):.3f} | "
        f"Precision={precision_score(y_train, pred, zero_division=0):.3f} | "
        f"Recall={recall_score(y_train, pred, zero_division=0):.3f} | "
        f"F1={f1_score(y_train, pred, zero_division=0):.3f}"
    )


# -----------------------------------
# 9. 임계값 직접 변경
# -----------------------------------
custom_threshold = 0.4

custom_pred = predict_threshold(
    model,
    X_train_scaled,
    custom_threshold
)

show_report(
    y_train,
    custom_pred,
    f"훈련 데이터 임계값 {custom_threshold} 평가"
)