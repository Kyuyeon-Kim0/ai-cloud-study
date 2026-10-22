"""Evaluate a fine-tuned ResNet18 on the held-out MNIST test set.
Run from the project root: python 05_evaluate.py
"""
import copy
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from tqdm.auto import tqdm

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / 'data'
OUTPUT_DIR = PROJECT_DIR / 'outputs'
# Keep this in sync with the checkpoint filename written by 04_train.py.
MODEL_PATH = OUTPUT_DIR / 'best_model_cpu_fast.pth'
BATCH_SIZE = 64
NUM_WORKERS = 0
SEED = 42
CLASS_NAMES = [str(i) for i in range(10)]

torch.manual_seed(SEED)
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_trained_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f'Missing checkpoint: {MODEL_PATH}')
    # Only load trusted checkpoints. weights_only=True avoids general pickle objects.
    checkpoint = torch.load(MODEL_PATH, map_location='cpu', weights_only=True)
    if checkpoint.get('num_classes') != 10:
        raise ValueError('Expected a checkpoint trained for 10 MNIST classes')
    if checkpoint.get('class_names') != CLASS_NAMES:
        raise ValueError('Checkpoint class names are not 0 through 9')
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 10)
    model.load_state_dict(checkpoint['model_state_dict'], strict=True)
    model.to(DEVICE).eval()
    return model, checkpoint


def load_test_data():
    # Exactly the same preprocessing as 04_train.py.
    transform = transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((112, 112)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    dataset = datasets.MNIST(root=str(DATA_DIR), train=False, download=True, transform=transform)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=NUM_WORKERS,
                        pin_memory=DEVICE.type == 'cuda')
    return dataset, loader


def evaluate(model, loader):
    actual, predicted = [], []
    with torch.inference_mode():
        for images, labels in tqdm(loader, desc='Evaluating', unit='batch'):
            logits = model(images.to(DEVICE))
            actual.extend(labels.tolist())
            predicted.extend(logits.argmax(dim=1).cpu().tolist())
    return np.asarray(actual), np.asarray(predicted)


def save_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=list(range(10)))
    fig, ax = plt.subplots(figsize=(9, 8))
    ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES).plot(ax=ax, cmap='Blues', values_format='d', colorbar=True)
    ax.set_title('MNIST ResNet18 - Test Confusion Matrix')
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'confusion_matrix.png', dpi=170)
    plt.close(fig)
    return cm


def save_misclassified(dataset, y_true, y_pred, max_examples=16):
    wrong = np.flatnonzero(y_true != y_pred)[:max_examples]
    fig, axes = plt.subplots(4, 4, figsize=(9, 9))
    for ax in axes.flat:
        ax.axis('off')
    for ax, idx in zip(axes.flat, wrong):
        raw_image, _ = dataset.data[idx].numpy(), dataset.targets[idx].item()
        ax.imshow(raw_image, cmap='gray', vmin=0, vmax=255)
        ax.set_title(f'True: {y_true[idx]} / Pred: {y_pred[idx]}', fontsize=10)
        ax.axis('off')
    fig.suptitle('Misclassified MNIST Test Images')
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'misclassified.png', dpi=170)
    plt.close(fig)


class GradCAM:
    """Grad-CAM on ResNet18 layer4 using activations and gradients."""
    def __init__(self, model):
        self.model = model
        self.activations = None
        self.gradients = None
        self.forward_handle = model.layer4.register_forward_hook(self._capture_activations)
        self.backward_handle = model.layer4.register_full_backward_hook(self._capture_gradients)

    def _capture_activations(self, module, inputs, output):
        self.activations = output.detach()

    def _capture_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, image, target_class):
        self.model.zero_grad(set_to_none=True)
        with torch.enable_grad():
            logits = self.model(image)
            logits[0, target_class].backward()
        if self.activations is None or self.gradients is None:
            raise RuntimeError('Grad-CAM hooks did not capture the required tensors')
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * self.activations).sum(dim=1, keepdim=True))
        cam = nn.functional.interpolate(cam, size=image.shape[-2:], mode='bilinear', align_corners=False)
        cam = cam[0, 0].cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam

    def close(self):
        self.forward_handle.remove()
        self.backward_handle.remove()


def save_gradcam(model, dataset, y_true, y_pred, examples=8):
    # Pick a mix of correct and incorrect predictions if available.
    correct = np.flatnonzero(y_true == y_pred)
    wrong = np.flatnonzero(y_true != y_pred)
    indices = list(correct[:min(4, len(correct))]) + list(wrong[:min(4, len(wrong))])
    if len(indices) < examples:
        used = set(indices)
        indices += [i for i in range(len(dataset)) if i not in used][:examples - len(indices)]
    indices = indices[:examples]

    cam_engine = GradCAM(model)
    fig, axes = plt.subplots(len(indices), 3, figsize=(9, 3 * len(indices)), squeeze=False)
    try:
        for row, idx in enumerate(tqdm(indices, desc='Generating Grad-CAM', unit='image')):
            tensor, _ = dataset[idx]
            tensor = tensor.unsqueeze(0).to(DEVICE)
            pred = int(y_pred[idx])
            cam = cam_engine.generate(tensor, target_class=pred)
            raw = dataset.data[idx].numpy()
            axes[row, 0].imshow(raw, cmap='gray', vmin=0, vmax=255)
            axes[row, 0].set_title(f'True {y_true[idx]} | Pred {pred}')
            axes[row, 1].imshow(cam, cmap='jet', vmin=0, vmax=1)
            axes[row, 1].set_title('Grad-CAM (predicted class)')
            axes[row, 2].imshow(raw, cmap='gray', vmin=0, vmax=255, extent=(0, 224, 224, 0))
            axes[row, 2].imshow(cam, cmap='jet', alpha=0.45, vmin=0, vmax=1, extent=(0, 224, 224, 0))
            axes[row, 2].set_title('Overlay')
            for ax in axes[row]:
                ax.axis('off')
    finally:
        cam_engine.close()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'gradcam.png', dpi=170)
    plt.close(fig)


def main():
    print('Device:', DEVICE)
    model, checkpoint = load_trained_model()
    dataset, loader = load_test_data()
    y_true, y_pred = evaluate(model, loader)
    accuracy = float(np.mean(y_true == y_pred))
    print(f'Test accuracy: {accuracy:.2%} ({(y_true == y_pred).sum()}/{len(y_true)})')
    report = classification_report(y_true, y_pred, labels=list(range(10)), target_names=CLASS_NAMES,
                                   output_dict=True, zero_division=0)
    print(classification_report(y_true, y_pred, labels=list(range(10)), target_names=CLASS_NAMES, zero_division=0))
    pd.DataFrame(report).T.to_csv(OUTPUT_DIR / 'classification_report.csv', encoding='utf-8-sig', index_label='class')
    cm = save_confusion_matrix(y_true, y_pred)
    save_misclassified(dataset, y_true, y_pred)
    save_gradcam(model, dataset, y_true, y_pred)
    evaluation = {
        'test_samples': int(len(y_true)),
        'test_accuracy': accuracy,
        'correct': int((y_true == y_pred).sum()),
        'incorrect': int((y_true != y_pred).sum()),
        'best_val_acc_from_checkpoint': float(checkpoint['best_val_acc']),
        'freeze_layers': checkpoint.get('freeze_layers', []),
        'train_layers': checkpoint.get('train_layers', []),
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
    }
    with (OUTPUT_DIR / 'evaluation.json').open('w', encoding='utf-8') as f:
        json.dump(evaluation, f, ensure_ascii=False, indent=2)
    print('\nSaved evaluation files to:', OUTPUT_DIR.resolve())


if __name__ == '__main__':
    main()
