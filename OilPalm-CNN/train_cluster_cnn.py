
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)

# Load patches and KMeans labels
X = np.load(BASE / "prepared_data" / "X_patches.npy").astype("float32")
df = pd.read_csv(RESULTS / "patch_clusters.csv")
y = df["cluster"].to_numpy(dtype=np.int64)

# Check dataset
assert len(X) == len(y), "Patch and label counts do not match"

# CNN architecture: 15 input bands, 3 output clusters
class ClusterCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(15, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(32, 3)
        )

    def forward(self, x):
        return self.net(x)

# Prepare tensors
X_tensor = torch.from_numpy(X)
y_tensor = torch.from_numpy(y)

dataset = TensorDataset(X_tensor, y_tensor)
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# Train
model = ClusterCNN()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

epochs = 50

for epoch in range(epochs):
    model.train()
    total_loss = 0

    for xb, yb in loader:
        optimizer.zero_grad()
        outputs = model(xb)
        loss = criterion(outputs, yb)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()

    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(loader):.4f}")

# Save model
torch.save(model.state_dict(), RESULTS / "cluster_cnn.pth")

print("\nCluster CNN training completed.")
print("Saved: results/cluster_cnn.pth")
print("This model reproduces KMeans cluster labels, not oil-palm labels.")
