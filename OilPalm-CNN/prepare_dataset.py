
from pathlib import Path

import numpy as np
import rasterio

# Project folders
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "prepared_data"

# Settings
PATCH_SIZE = 32
STRIDE = 32

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

tif_files = sorted(
    p for p in DATA_DIR.glob("*.tif")
    if p.name != "AP_Sentinel2_2024_AllBands_Test.tif"
)

if not tif_files:
    raise FileNotFoundError(f"No satellite TIFF files found in {DATA_DIR}")

all_patches = []
patch_sources = []

for image_path in tif_files:
    print(f"\nProcessing: {image_path.name}")

    with rasterio.open(image_path) as src:
        image = src.read(masked=True).astype(np.float32)
        image = image.filled(np.nan)

    # Expected layout: bands, height, width
    bands, height, width = image.shape
    print(f"Image shape: {image.shape}")

    # Normalize each band independently, using valid pixels.
    normalized = np.zeros_like(image, dtype=np.float32)

    for b in range(bands):
        band = image[b]
        valid = np.isfinite(band)

        if not valid.any():
            continue

        low, high = np.percentile(band[valid], [2, 98])

        if high > low:
            normalized[b, valid] = np.clip(
                (band[valid] - low) / (high - low), 0, 1
            )

    count = 0

    for row in range(0, height - PATCH_SIZE + 1, STRIDE):
        for col in range(0, width - PATCH_SIZE + 1, STRIDE):
            patch = normalized[
                :, row:row + PATCH_SIZE, col:col + PATCH_SIZE
            ]

            # Skip patches with too many invalid pixels.
            original_patch = image[
                :, row:row + PATCH_SIZE, col:col + PATCH_SIZE
            ]
            valid_fraction = np.isfinite(original_patch).mean()

            if valid_fraction < 0.95:
                continue

            all_patches.append(patch)
            patch_sources.append(image_path.name)
            count += 1

    print(f"Valid patches created: {count}")

if not all_patches:
    raise ValueError(
        "No patches were created. Check the TIFF dimensions and valid pixels."
    )

X = np.stack(all_patches).astype(np.float32)

# Shape: (number of patches, bands, 32, 32)
np.save(OUTPUT_DIR / "X_patches.npy", X)
np.save(
    OUTPUT_DIR / "patch_sources.npy",
    np.array(patch_sources)
)

print("\nDataset preparation complete!")
print("Patch array shape:", X.shape)
print("Number of bands:", X.shape[1])
print("Patch size:", PATCH_SIZE, "x", PATCH_SIZE)
print("Saved to:", OUTPUT_DIR)
print("\nNote: These patches do not yet have oil-palm class labels.")
