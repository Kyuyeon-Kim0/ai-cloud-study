import math

# 학습 데이터
x = [1, 2, 3]
y = [0, 0, 1]

def sigmoid(z):
    return 1 / (1 + math.exp(-z))

# 학습률별 실험
for lr in [0.001, 0.1, 1, 10]:
    w, b = 0.0, 0.0

    print(f"\n학습률: {lr}")

    for epoch in range(100):
        dw, db = 0, 0
        loss = 0

        for xi, yi in zip(x, y):
            pred = sigmoid(w * xi + b)
            error = pred - yi

            dw += error * xi
            db += error

            # 교차 엔트로피 손실
            loss += -(yi * math.log(pred + 1e-10)
                      + (1 - yi) * math.log(1 - pred + 1e-10))

        w -= lr * dw / 3
        b -= lr * db / 3

        if epoch % 10 == 0:
            print(f"epoch={epoch}, loss={loss/3:.4f}")