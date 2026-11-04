
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data" / "AP_Hansen_GFC_2025.tif"
OUTPUT = ROOT / "results"
OUTPUT.mkdir(parents=True, exist_ok=True)

if not INPUT.exists():
    raise FileNotFoundError(
        f"Forest-loss raster not found:\n{INPUT}\n"
        "Download the GeoTIFF from Google Drive and put it "
        "inside forest_loss/data/."
    )

# Approximate baseline canopy threshold for analysis.
# This is a configurable tree-cover threshold, not a
# definitive natural-forest classification.
TREE_COVER_THRESHOLD = 30

with rasterio.open(INPUT) as src:
    print("Input:", INPUT.name)
    print("CRS:", src.crs)
    print("Dimensions:", src.width, "x", src.height)
    print("Bands:", src.count)
    print("Band descriptions:", src.descriptions)
    print("Pixel size:", src.res)

    if src.count < 2:
        raise ValueError(
            "Expected two bands: treecover2000 and lossyear."
        )

    tree_cover = src.read(1)
    loss_year = src.read(2)

    # This export should contain the two requested bands.
    # Check the metadata before interpreting their order.
    descriptions = list(src.descriptions)
    if descriptions[0] and descriptions[0] != "treecover2000":
        raise ValueError(
            "Band 1 is not treecover2000. "
            f"Found: {descriptions[0]}"
        )
    if descriptions[1] and descriptions[1] != "lossyear":
        raise ValueError(
            "Band 2 is not lossyear. "
            f"Found: {descriptions[1]}"
        )

    transform = src.transform
    pixel_area_ha = abs(
        transform.a * transform.e -
        transform.b * transform.d
    ) / 10000.0

    # EPSG:32644 uses metres, so the determinant above
    # gives square metres per pixel before conversion to ha.
    valid = (
        (tree_cover != src.nodata)
        if src.nodata is not None
        else np.ones(tree_cover.shape, dtype=bool)
    )

    valid &= (
        (loss_year != src.nodata)
        if src.nodata is not None
        else np.ones(loss_year.shape, dtype=bool)
    )

    valid &= np.isfinite(tree_cover) & np.isfinite(loss_year)

    baseline_tree = valid & (
        tree_cover >= TREE_COVER_THRESHOLD
    )

    # The loss year band uses 1=2001, ..., 25=2025.
    records = []

    for code in range(1, 26):
        year = 2000 + code

        loss_pixels = (
            valid
            & (loss_year == code)
        )

        baseline_tree_loss_pixels = (
            loss_pixels & baseline_tree
        )

        records.append({
            "year": year,
            "all_tree_cover_loss_pixels": int(
                loss_pixels.sum()
            ),
            "all_tree_cover_loss_ha": float(
                loss_pixels.sum() * pixel_area_ha
            ),
            "loss_pixels_in_2000_treecover_threshold": int(
                baseline_tree_loss_pixels.sum()
            ),
            "loss_ha_in_2000_treecover_threshold": float(
                baseline_tree_loss_pixels.sum()
                * pixel_area_ha
            )
        })

summary = pd.DataFrame(records)

csv_path = OUTPUT / "annual_tree_cover_loss.csv"
summary.to_csv(csv_path, index=False)

# Save a map of the recorded loss years.
display_loss = np.where(
    valid & (loss_year > 0),
    loss_year,
    np.nan
)

fig, ax = plt.subplots(figsize=(9, 7))
im = ax.imshow(
    display_loss,
    cmap="YlOrRd",
    vmin=1,
    vmax=25
)
ax.set_title("Hansen tree-cover loss year (2001-2025)")
ax.set_xlabel("Pixel column")
ax.set_ylabel("Pixel row")
fig.colorbar(im, ax=ax, label="Year code (1=2001, 25=2025)")
fig.tight_layout()

map_path = OUTPUT / "tree_cover_loss_year_map.png"
fig.savefig(map_path, dpi=160)
plt.close(fig)

print("\nANNUAL TREE-COVER LOSS SUMMARY")
print(summary.to_string(index=False))
print("\nCSV saved:", csv_path)
print("Map saved:", map_path)
print(f"Pixel area: {pixel_area_ha:.4f} hectares")

print(
    "\nInterpretation note: these are dataset-derived tree-cover "
    "loss estimates, not verified natural-forest deforestation "
    "or oil-palm-caused loss."
)
