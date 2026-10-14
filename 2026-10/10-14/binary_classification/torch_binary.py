import copy
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from torch.utils.data import DataLoader, TensorDataset

# ==================================================
# 1. 기본 설정
# ==================================================
torch.manual_seed(42)

EPOCHS = 200
BATCH_SIZE = 4
LR = 0.01

PATIENCE = 15       # 개선되지 않는 Epoch 허용 횟수
MIN_DELTA = 0.0001  # 최소 개선량

# ==================================================
# 2. 데이터 생성 (X 3개, Y 1개)
# ==================================================
X = torch.tensor([
    [1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5, 6],
    [5, 6, 7], [6, 7, 8], [7, 8, 9], [8, 9, 10],
    [9, 10, 11], [10, 11, 12], [11, 12, 13],
    [12, 13, 14], [13, 14, 15], [14, 15, 16],
    [15, 16, 17], [16, 17, 18], [17, 18, 19],
    [18, 19, 20], [19, 20, 21], [20, 21, 22]
], dtype=torch.float32)

Y = torch.tensor(
    [[0]] * 10 + [[1]] * 10,
    dtype=torch.float32
)

# ==================================================
# 3. Train / Validation / Test 분리
#    각 그룹에 0과 1이 동일하게 포함되도록 분리
# ==================================================
idx0 = torch.randperm(10)
idx1 = torch.randperm(10) + 10

train_idx = torch.cat([idx0[:6], idx1[:6]])
val_idx = torch.cat([idx0[6:8], idx1[6:8]])
test_idx = torch.cat([idx0[8:], idx1[8:]])

X_train, Y_train = X[train_idx], Y[train_idx]
X_val, Y_val = X[val_idx], Y[val_idx]
X_test, Y_test = X[test_idx], Y[test_idx]

# 훈련 데이터 기준으로만 정규화
mean = X_train.mean(dim=0)
std = X_train.std(dim=0).clamp(min=1e-6)

X_train = (X_train - mean) / std
X_val = (X_val - mean) / std
X_test = (X_test - mean) / std

train_loader = DataLoader(
    TensorDataset(X_train, Y_train),
    batch_size=BATCH_SIZE,
    shuffle=True
)

# ==================================================
# 4. 신경망 모델
#    BCEWithLogitsLoss를 사용하므로 Sigmoid 제외
# ==================================================
model = nn.Sequential(
    nn.Linear(3, 8),
    nn.ReLU(),

    nn.Linear(8, 4),
    nn.ReLU(),

    nn.Linear(4, 1)
)

# ==================================================
# 5. 손실함수 / 최적화
# ==================================================
loss_fn = nn.BCEWithLogitsLoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LR
)

# ==================================================
# 6. Early Stopping 변수
# ==================================================
best_loss = float("inf")
best_epoch = 0
wait = 0

train_losses = []
val_losses = []

# ==================================================
# 7. 학습
# ==================================================
for epoch in range(EPOCHS):

    # ---------- 훈련 ----------
    model.train()

    total_loss = 0

    for xb, yb in train_loader:

        pred = model(xb)
        loss = loss_fn(pred, yb)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(xb)

    train_loss = total_loss / len(X_train)

    # ---------- 검증 ----------
    model.eval()

    with torch.no_grad():
        val_pred = model(X_val)
        val_loss = loss_fn(val_pred, Y_val).item()

    # ---------- 히스토리 저장 ----------
    train_losses.append(train_loss)
    val_losses.append(val_loss)

    print(
        f"Epoch {epoch+1:3d} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f}"
    )

    # ---------- Best Model 저장 ----------
    if val_loss < best_loss - MIN_DELTA:

        best_loss = val_loss
        best_epoch = epoch + 1
        wait = 0

        torch.save({
            "model_state_dict": model.state_dict(),
            "mean": mean,
            "std": std,
            "best_epoch": best_epoch,
            "best_val_loss": best_loss
        }, "best_model.pt")

        print("  → Best Model 저장!")

    else:
        wait += 1

    # ---------- Early Stopping ----------
    if wait >= PATIENCE:
        print(f"\nEarly Stopping! Epoch {epoch+1}")
        break

# ==================================================
# 8. Best Model 불러오기
# ==================================================
checkpoint = torch.load(
    "best_model.pt",
    map_location="cpu",
    weights_only=True
)

model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

print(f"\nBest Epoch: {best_epoch}")
print(f"Best Validation Loss: {best_loss:.4f}")

# ==================================================
# 9. 테스트 (학습 완료 후 한 번만)
# ==================================================
with torch.no_grad():

    logits = model(X_test)
    test_loss = loss_fn(logits, Y_test).item()

    probabilities = torch.sigmoid(logits)
    predictions = (probabilities >= 0.5).float()

    accuracy = (predictions == Y_test).float().mean()

print("\n===== Test Result =====")
print(f"Test Loss: {test_loss:.4f}")
print(f"Test Accuracy: {accuracy.item()*100:.2f}%")

for x, y, p in zip(X_test, Y_test, probabilities):
    print(
        f"X={x.tolist()} | "
        f"정답={int(y.item())} | "
        f"예측확률={p.item():.4f}"
    )

# ==================================================
# 10. Train / Validation Loss 차트
# ==================================================
plt.figure(figsize=(9, 5))

plt.plot(
    train_losses,
    label="Train Loss"
)

plt.plot(
    val_losses,
    label="Validation Loss"
)

plt.axvline(
    best_epoch - 1,
    color="red",
    linestyle="--",
    label=f"Best Epoch: {best_epoch}"
)

plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.title("Training / Validation Loss")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("training_history.png", dpi=150)
plt.show()