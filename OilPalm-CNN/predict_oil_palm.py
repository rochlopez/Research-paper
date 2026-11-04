
from pathlib import Path

import numpy as np
import rasterio
import torch
from torch import nn

ROOT = Path(".")
DATA = ROOT / "data"
RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)

MODEL_PATH = RESULTS / "supervised_cnn_final.pth"
PATCH_SIZE = 32
device = torch.device("cpu")


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


checkpoint = torch.load(
    MODEL_PATH, map_location=device, weights_only=True
)

model = SmallCNN().to(device)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

mean = checkpoint["mean"]
std = checkpoint["std"]

tile_paths = sorted(DATA.glob("AP_Sentinel2_2024_Tile_*.tif"))

if not tile_paths:
    raise FileNotFoundError(
        "No satellite tiles found in the data folder."
    )

for tile_path in tile_paths:
    with rasterio.open(tile_path) as src:
        image = src.read().astype(np.float32)
        profile = src.profile.copy()
        height, width = src.height, src.width

    if image.shape[0] != 15:
        raise ValueError(
            f"{tile_path.name} has {image.shape[0]} bands; expected 15."
        )

    # Use the same channel-wise normalization as training.
    image_tensor = torch.from_numpy(image).unsqueeze(0)
    image_tensor = (image_tensor - mean) / std

    # Predict a class for each complete, non-overlapping 32x32 patch.
    prediction_map = np.full((height, width), 255, dtype=np.uint8)
    probability_map = np.full((height, width), -9999, dtype=np.float32)

    with torch.no_grad():
        for row in range(0, height - PATCH_SIZE + 1, PATCH_SIZE):
            for col in range(0, width - PATCH_SIZE + 1, PATCH_SIZE):
                patch = image_tensor[
                    :, :, row:row + PATCH_SIZE, col:col + PATCH_SIZE
                ]

                probabilities = torch.softmax(model(patch), dim=1)
                palm_probability = probabilities[0, 1].item()
                predicted_class = int(palm_probability >= 0.5)

                prediction_map[
                    row:row + PATCH_SIZE, col:col + PATCH_SIZE
                ] = predicted_class

                probability_map[
                    row:row + PATCH_SIZE, col:col + PATCH_SIZE
                ] = palm_probability

    out_profile = profile.copy()
    out_profile.update(
        count=1,
        dtype="uint8",
        nodata=255,
        compress="lzw"
    )

    prediction_path = RESULTS / f"{tile_path.stem}_prediction.tif"
    with rasterio.open(prediction_path, "w", **out_profile) as dst:
        dst.write(prediction_map, 1)

    prob_profile = profile.copy()
    prob_profile.update(
        count=1,
        dtype="float32",
        nodata=-9999.0,
        compress="lzw"
    )

    probability_path = RESULTS / f"{tile_path.stem}_probability.tif"
    with rasterio.open(probability_path, "w", **prob_profile) as dst:
        dst.write(probability_map, 1)

    valid = prediction_map != 255
    if valid.any():
        positive_fraction = np.mean(prediction_map[valid] == 1)
        print(f"\n{tile_path.name}")
        print(f"Predicted oil-palm patch area fraction: {positive_fraction:.1%}")
        print(f"Saved: {prediction_path}")
        print(f"Saved: {probability_path}")

print("\nPrediction complete.")
