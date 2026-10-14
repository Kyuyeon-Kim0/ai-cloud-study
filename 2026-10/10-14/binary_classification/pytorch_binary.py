import torch
import torch.nn as nn

# 1. 학습 데이터 (20개 × 특성 3개)
X = torch.tensor([
    [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6],
    [5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9, 10],
    [9, 10, 11], [10, 11, 12], [11, 12, 13],
    [12, 13, 14], [13, 14, 15], [14, 15, 16],
    [15, 16, 17], [16, 17, 18], [17, 18, 19],
    [18, 19, 20], [19, 20, 21], [20, 21, 22]
], dtype=torch.float32)

# 2. 정답 Y (0 또는 1)
Y = torch.tensor([
    [0], [0], [0], [0], [0],
    [0], [0], [0], [0], [0],
    [1], [1], [1], [1], [1],
    [1], [1], [1], [1], [1]
], dtype=torch.float32)

# 3. 모델 생성
torch.manual_seed(42)

model = nn.Sequential(
    nn.Linear(3, 8),   # 입력 3개 → 히든 8개
    nn.ReLU(),

    nn.Linear(8, 4),   # 히든 8개 → 히든 4개
    nn.ReLU(),

    nn.Linear(4, 1),   # 히든 4개 → 출력 1개
    nn.Sigmoid()
)

# 4. 손실함수와 최적화
loss_fn = nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

# 5. 학습 전 W, B 저장
before = {
    name: param.detach().clone()
    for name, param in model.named_parameters()
}

# 6. 학습 (Epoch 2회, Batch Size 4)
for epoch in range(2):

    for i in range(0, 20, 4):

        x_batch = X[i:i+4]
        y_batch = Y[i:i+4]

        # 순전파: 예측
        pred = model(x_batch)

        # 손실 계산
        loss = loss_fn(pred, y_batch)

        # 역전파 및 가중치 업데이트
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        print(
            f"Epoch {epoch+1}, "
            f"Batch {i//4+1}, "
            f"Loss {loss.item():.4f}"
        )

# 7. 학습 전후 W, B 비교
print("\n===== 학습 전후 W, B 비교 =====")

for name, param in model.named_parameters():

    old = before[name]
    new = param.detach()

    print(f"\n{name}")
    print("학습 전:\n", old)
    print("학습 후:\n", new)
    print("변화량:\n", new - old)

# 8. 최종 이진분류 예측
print("\n===== 최종 예측 결과 =====")

with torch.no_grad():

    prob = model(X)
    result = (prob >= 0.5).int()

    for x, y, p, r in zip(X, Y, prob, result):
        print(
            f"X={x.tolist()}, "
            f"정답={int(y.item())}, "
            f"확률={p.item():.4f}, "
            f"예측={r.item()}"
        )

    # 정확도 계산
    accuracy = (result == Y.int()).float().mean()

    print(f"\n정확도: {accuracy.item()*100:.2f}%")