"""MNIST ResNet18 CPU quick experiment using GPT freeze_analysis.json."""
import copy
import json
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms
from tqdm.auto import tqdm

DATA_DIR = Path('data')
OUTPUT_DIR = Path('outputs')
JSON_PATH = OUTPUT_DIR / 'freeze_analysis.json'
EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 1e-4
SEED = 42
IMAGE_SIZE = 112
DEVICE = torch.device('cpu')
LAYER_ORDER = ['conv1', 'bn1', 'layer1', 'layer2', 'layer3', 'layer4', 'fc']


def load_layer_settings(path: Path):
    with path.open('r', encoding='utf-8') as file:
        data = json.load(file)
    frozen = data['freeze_layers']
    trainable = data['train_layers']
    fs, ts = set(frozen), set(trainable)
    if (len(fs) != len(frozen) or len(ts) != len(trainable)
            or fs & ts or fs | ts != set(LAYER_ORDER) or 'fc' not in ts):
        raise ValueError('Invalid freeze/train layer partition in GPT JSON')
    if ('conv1' in ts) != ('bn1' in ts):
        raise ValueError('conv1 and bn1 must share train/freeze status')
    started = False
    for name in LAYER_ORDER:
        if name in ts:
            started = True
        elif started:
            raise ValueError('Train layers must form a contiguous suffix')
    return frozen, trainable


def keep_frozen_batchnorm_eval(model: nn.Module, train_layers: list[str]):
    train_set = set(train_layers)
    for name, module in model.named_modules():
        if isinstance(module, nn.modules.batchnorm._BatchNorm):
            belongs_to_trainable = any(
                name == layer or name.startswith(layer + '.') for layer in train_set
            )
            if not belongs_to_trainable:
                module.eval()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(SEED)
    frozen, trainable = load_layer_settings(JSON_PATH)
    print('Device:', DEVICE, flush=True)
    print('Frozen:', frozen, flush=True)
    print('Trainable:', trainable, flush=True)

    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    dataset = datasets.MNIST(root=str(DATA_DIR), train=True, download=True, transform=transform)
    indices = torch.randperm(len(dataset), generator=torch.Generator().manual_seed(SEED))[:6000].tolist()
    train_data = Subset(dataset, indices[:5000])
    val_data = Subset(dataset, indices[5000:])
    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(model.fc.in_features, 10)
    for param in model.parameters():
        param.requires_grad = False
    for name in trainable:
        for param in getattr(model, name).parameters():
            param.requires_grad = True
    model.to(DEVICE)
    print('\n===== Actual layer settings =====', flush=True)
    for name in LAYER_ORDER:
        is_trainable = any(p.requires_grad for p in getattr(model, name).parameters())
        print(f'{name:8s}: {"TRAIN" if is_trainable else "FREEZE"}', flush=True)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW((p for p in model.parameters() if p.requires_grad), lr=LEARNING_RATE)
    history = []
    best_acc = -1.0
    for epoch in range(1, EPOCHS + 1):
        model.train()
        keep_frozen_batchnorm_eval(model, trainable)
        train_loss_sum = 0.0
        train_correct = 0
        progress = tqdm(train_loader, desc=f'Epoch {epoch}/{EPOCHS} train', unit='batch')
        for images, labels in progress:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss_sum += loss.item() * labels.size(0)
            train_correct += (outputs.argmax(dim=1) == labels).sum().item()
            progress.set_postfix(loss=f'{train_loss_sum / ((progress.n + 1) * BATCH_SIZE):.3f}')

        model.eval()
        val_loss_sum = 0.0
        val_correct = 0
        with torch.inference_mode():
            for images, labels in tqdm(val_loader, desc=f'Epoch {epoch}/{EPOCHS} val', unit='batch'):
                outputs = model(images.to(DEVICE))
                labels = labels.to(DEVICE)
                loss = criterion(outputs, labels)
                val_loss_sum += loss.item() * labels.size(0)
                val_correct += (outputs.argmax(dim=1) == labels).sum().item()
        record = {
            'epoch': epoch,
            'train_loss': train_loss_sum / len(train_data),
            'train_acc': train_correct / len(train_data),
            'val_loss': val_loss_sum / len(val_data),
            'val_acc': val_correct / len(val_data),
        }
        history.append(record)
        print(f'Epoch {epoch}: train_acc={record["train_acc"]:.2%}, '
              f'val_acc={record["val_acc"]:.2%}, val_loss={record["val_loss"]:.4f}', flush=True)
        if record['val_acc'] > best_acc:
            best_acc = record['val_acc']
            torch.save({
                'model_state_dict': copy.deepcopy(model.state_dict()),
                'num_classes': 10,
                'class_names': [str(i) for i in range(10)],
                'freeze_layers': frozen,
                'train_layers': trainable,
                'best_val_acc': best_acc,
                'epoch': epoch,
                'image_size': IMAGE_SIZE,
                'experiment': 'cpu_fast_5000_1000',
            }, OUTPUT_DIR / 'best_model_cpu_fast.pth')
            print('Saved best model: outputs/best_model_cpu_fast.pth', flush=True)
        with (OUTPUT_DIR / 'training_history_cpu_fast.json').open('w', encoding='utf-8') as file:
            json.dump(history, file, ensure_ascii=False, indent=2)
    print(f'Completed. Best validation accuracy: {best_acc:.2%}', flush=True)


if __name__ == '__main__':
    main()
