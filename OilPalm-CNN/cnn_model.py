
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

PROJECT_DIR = Path(__file__).resolve().parent
DATA_FILE = PROJECT_DIR / "prepared_data" / "X_patches.npy"

# Load prepared satellite patches
X = np.load(DATA_FILE).astype(np.float32)

print("Loaded patches:", X.shape)

# CNN expects (batch, channels, height, width)
X_tensor = torch.from_numpy(X)

class OilPalmCNN(nn.Module):
    def __init__(self, input_bands=15):
        super().__init__()

        self.features = nn.Sequential(
            nn.Conv2d(input_bands, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.classifier = nn.Linear(64, 2)

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, start_dim=1)
        return self.classifier(x)

model = OilPalmCNN(input_bands=X.shape[1])

# Test a forward pass; this does not train the model
model.eval()
with torch.no_grad():
    sample = X_tensor[:4]
    output = model(sample)

print("Model output shape:", output.shape)
print("CNN architecture test passed!")
print("Output values are untrained scores, not predictions.")
