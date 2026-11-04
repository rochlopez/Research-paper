
from pathlib import Path
import copy
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)

ROOT = Path(".")
DATA = ROOT / "prepared_data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

X = np.load(DATA / "X_patches_thresholded.npy")
y = np.load(DATA / "y_labels_thresholded.npy")
metadata = pd.read_csv(DATA / "thresholded_patch_labels.csv")

torch.manual_seed(42)
np.random.seed(42)
device = torch.device("cpu")

# Convert to NCHW and standardize each channel using training tiles only.
X = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.long)

class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(15, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        return self.features(x)

all_tiles = metadata["tile"].to_numpy()
tile_names = sorted(metadata["tile"].unique())
all_results = []
fold_models = {}

for held_out in tile_names:
    test_idx = np.where(all_tiles == held_out)[0]
    train_idx = np.where(all_tiles != held_out)[0]

    if len(np.unique(y[train_idx])) < 2:
        print(f"Skipping {held_out}: training set lacks a class.")
        continue

    # Per-band normalization based only on training patches.
    train_x = X[train_idx]
    mean = train_x.mean(dim=(0, 2, 3), keepdim=True)
    std = train_x.std(dim=(0, 2, 3), keepdim=True).clamp_min(1e-6)

    train_x = (train_x - mean) / std
    test_x = (X[test_idx] - mean) / std

    # Inverse-frequency class weights from training data.
    class_counts = np.bincount(y[train_idx], minlength=2)
    weights = torch.tensor(
        len(train_idx) / (2 * np.maximum(class_counts, 1)),
        dtype=torch.float32
    )

    model = SmallCNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.CrossEntropyLoss(weight=weights)

    train_ds = TensorDataset(train_x, y_tensor[train_idx])
    loader = DataLoader(train_ds, batch_size=16, shuffle=True)

    model.train()
    for epoch in range(30):
        for xb, yb in loader:
            optimizer.zero_grad()
            loss = loss_fn(model(xb), yb)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        probabilities = torch.softmax(model(test_x), dim=1)[:, 1].numpy()
        predictions = (probabilities >= 0.5).astype(int)

    truth = y[test_idx]
    result = {
        "held_out_tile": held_out,
        "train_patches": len(train_idx),
        "test_patches": len(test_idx),
        "accuracy": accuracy_score(truth, predictions),
        "precision": precision_score(truth, predictions, zero_division=0),
        "recall": recall_score(truth, predictions, zero_division=0),
        "f1": f1_score(truth, predictions, zero_division=0),
        "confusion_matrix": confusion_matrix(
            truth, predictions, labels=[0, 1]
        ).tolist()
    }
    all_results.append(result)
    fold_models[held_out] = {
        "state_dict": copy.deepcopy(model.state_dict()),
        "mean": mean,
        "std": std
    }

    print("\nHeld-out tile:", held_out)
    for key, value in result.items():
        print(f"{key}: {value}")

pd.DataFrame(all_results).to_csv(
    RESULTS / "supervised_cnn_tile_evaluation.csv", index=False
)

print("\nSaved evaluation:", RESULTS / "supervised_cnn_tile_evaluation.csv")
print("These are preliminary results against historical reference labels.")



# Train the final model on all prepared patches and save it.

X_all = torch.tensor(
    np.load(DATA / "X_patches_thresholded.npy"),
    dtype=torch.float32
)
y_all = torch.tensor(
    np.load(DATA / "y_labels_thresholded.npy"),
    dtype=torch.long
)

# Calculate normalization values from the full training dataset.
final_mean = X_all.mean(dim=(0, 2, 3), keepdim=True)
final_std = X_all.std(dim=(0, 2, 3), keepdim=True).clamp_min(1e-6)
X_normalized = (X_all - final_mean) / final_std

final_model = SmallCNN().to(device)
final_optimizer = torch.optim.Adam(final_model.parameters(), lr=0.001)

counts = np.bincount(y_all.numpy(), minlength=2)
class_weights = torch.tensor(
    len(y_all) / (2 * np.maximum(counts, 1)),
    dtype=torch.float32
)
final_loss_fn = nn.CrossEntropyLoss(weight=class_weights)

final_loader = DataLoader(
    TensorDataset(X_normalized, y_all),
    batch_size=16,
    shuffle=True
)

final_model.train()
for epoch in range(30):
    total_loss = 0.0
    for xb, yb in final_loader:
        final_optimizer.zero_grad()
        loss = final_loss_fn(final_model(xb), yb)
        loss.backward()
        final_optimizer.step()
        total_loss += loss.item()

    if (epoch + 1) % 5 == 0:
        print(
            f"Final training epoch {epoch + 1}/50, "
            f"loss={total_loss / len(final_loader):.4f}"
        )

model_path = RESULTS / "supervised_cnn_final.pth"
torch.save(
    {
        "model_state_dict": final_model.state_dict(),
        "mean": final_mean,
        "std": final_std,
        "input_bands": [
            "B1", "B2", "B3", "B4", "B5", "B6", "B7",
            "B8", "B8A", "B9", "B11", "B12",
            "NDVI", "NDMI", "EVI"
        ],
        "classes": {
            0: "Low oil-palm reference fraction",
            1: "High oil-palm reference fraction"
        }
    },
    model_path
)

print(f"Final model saved to: {model_path}")

