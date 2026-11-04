

from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

BASE = Path(__file__).resolve().parent
X = np.load(BASE / "prepared_data" / "X_patches.npy").astype("float32")

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

model = ClusterCNN()
weights = BASE / "results" / "cluster_cnn.pth"
model.load_state_dict(
    torch.load(weights, map_location="cpu", weights_only=True)
)
model.eval()

with torch.no_grad():
    probabilities = torch.softmax(model(torch.from_numpy(X)), dim=1)
    confidence, predicted = probabilities.max(dim=1)

result = pd.DataFrame({
    "patch_id": np.arange(len(X)),
    "predicted_cluster": predicted.numpy(),
    "confidence": confidence.numpy().round(4)
})

output = BASE / "results" / "cluster_predictions.csv"
result.to_csv(output, index=False)

print(result.head(10).to_string(index=False))
print(f"\nSaved predictions to: {output}")
print("These are cluster predictions, not oil-palm predictions.")
