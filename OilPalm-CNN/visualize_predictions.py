
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio

ROOT = Path(".")
DATA = ROOT / "data"
RESULTS = ROOT / "results"

tiles = sorted(DATA.glob("AP_Sentinel2_2024_Tile_*.tif"))

fig, axes = plt.subplots(len(tiles), 3, figsize=(14, 4 * len(tiles)))

for i, tile_path in enumerate(tiles):
    prediction_path = RESULTS / f"{tile_path.stem}_prediction.tif"
    probability_path = RESULTS / f"{tile_path.stem}_probability.tif"

    with rasterio.open(tile_path) as src:
        # Sentinel-2 RGB: B4 red, B3 green, B2 blue.
        rgb = src.read([4, 3, 2]).astype(np.float32)
        rgb = np.moveaxis(rgb, 0, -1)

    # Percentile stretch for a clearer RGB display.
    for band in range(3):
        low, high = np.nanpercentile(rgb[:, :, band], [2, 98])
        rgb[:, :, band] = np.clip(
            (rgb[:, :, band] - low) / max(high - low, 1e-6), 0, 1
        )

    with rasterio.open(prediction_path) as src:
        prediction = src.read(1)
        nodata = src.nodata

    with rasterio.open(probability_path) as src:
        probability = src.read(1)
        probability_nodata = src.nodata

    pred_masked = np.ma.masked_where(
        (prediction == nodata) | (prediction == 255), prediction
    )
    prob_masked = np.ma.masked_where(
        probability == probability_nodata, probability
    )

    axes[i, 0].imshow(rgb)
    axes[i, 0].set_title(f"{tile_path.stem}\nSatellite RGB")

    axes[i, 1].imshow(pred_masked, vmin=0, vmax=1, cmap="RdYlGn_r")
    axes[i, 1].set_title("CNN class prediction\n0 = non-palm, 1 = palm")

    image = axes[i, 2].imshow(
        prob_masked, vmin=0, vmax=1, cmap="viridis"
    )
    axes[i, 2].set_title("Estimated oil-palm probability")
    fig.colorbar(image, ax=axes[i, 2], fraction=0.046, pad=0.04)

    for ax in axes[i]:
        ax.set_xticks([])
        ax.set_yticks([])

plt.tight_layout()
output_path = RESULTS / "prediction_visualization.png"
plt.savefig(output_path, dpi=180, bbox_inches="tight")
plt.show()

print(f"Saved visualization to: {output_path}")
