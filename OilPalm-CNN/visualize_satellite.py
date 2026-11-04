
from pathlib import Path

import numpy as np
import rasterio
import matplotlib.pyplot as plt


# Project folders
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

# Select one satellite tile
image_path = DATA_DIR / "AP_Sentinel2_2024_Tile_1.tif"

with rasterio.open(image_path) as src:
    # Read Red, Green, Blue bands
    # Sentinel-2 band indexes:
    # B2 = Blue (band 2)
    # B3 = Green (band 3)
    # B4 = Red (band 4)
    blue = src.read(2, masked=True).astype("float32")
    green = src.read(3, masked=True).astype("float32")
    red = src.read(4, masked=True).astype("float32")

    # Convert reflectance values for display
    rgb = np.ma.stack([red, green, blue], axis=-1)
    rgb = rgb.filled(np.nan)

    # Percentile stretch improves image visibility
    valid = rgb[np.isfinite(rgb)]
    if valid.size == 0:
        raise ValueError("The image contains no valid RGB pixels.")

    low, high = np.nanpercentile(valid, [2, 98])
    rgb = np.clip((rgb - low) / max(high - low, 1e-6), 0, 1)

    # Read vegetation indices
    ndvi = src.read(13, masked=True).astype("float32")
    ndmi = src.read(14, masked=True).astype("float32")
    evi = src.read(15, masked=True).astype("float32")

fig, axes = plt.subplots(1, 4, figsize=(18, 5))

axes[0].imshow(rgb)
axes[0].set_title("True Colour (RGB)")

im1 = axes[1].imshow(ndvi, cmap="RdYlGn", vmin=-1, vmax=1)
axes[1].set_title("NDVI")
fig.colorbar(im1, ax=axes[1], fraction=0.046)

im2 = axes[2].imshow(ndmi, cmap="BrBG", vmin=-1, vmax=1)
axes[2].set_title("NDMI")
fig.colorbar(im2, ax=axes[2], fraction=0.046)

im3 = axes[3].imshow(evi, cmap="YlGn", vmin=-1, vmax=1)
axes[3].set_title("EVI")
fig.colorbar(im3, ax=axes[3], fraction=0.046)

for ax in axes:
    ax.axis("off")

plt.suptitle("Oil Palm Project: Sentinel-2 Satellite Tile 1")
plt.tight_layout()
plt.show()