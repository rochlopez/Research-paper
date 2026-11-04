
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt


# ============================================================
# 1. PROJECT PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "OilPalm-CNN" / "data"
OUTPUT_DIR = ROOT / "forest_loss" / "results"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. SETTINGS
# ============================================================

YEAR = 2024
INDEX_NAMES = ["NDVI", "NDMI", "EVI"]

# NDVI thresholds used only for a simple vegetation-condition
# visualization. These are not universal forest classifications.
NDVI_LOW = 0.20
NDVI_HIGH = 0.50


# ============================================================
# 3. FIND INPUT SATELLITE TILES
# ============================================================

tiles = sorted(DATA_DIR.glob(f"AP_Sentinel2_{YEAR}_Tile_*.tif"))

if not tiles:
    raise FileNotFoundError(
        f"No satellite tiles found in:\n{DATA_DIR}\n"
        "Check your folder paths and TIFF filenames."
    )

print("=" * 60)
print("OIL-PALM PROJECT: VEGETATION BASELINE")
print("=" * 60)
print(f"Year: {YEAR}")
print(f"Tiles found: {len(tiles)}")
print(f"Output folder: {OUTPUT_DIR}")


# ============================================================
# 4. ANALYZE EACH TILE
# ============================================================

records = []

for tile_path in tiles:

    print(f"\nProcessing: {tile_path.name}")

    with rasterio.open(tile_path) as src:

        band_names = list(src.descriptions)

        missing = [
            name for name in INDEX_NAMES
            if name not in band_names
        ]

        if missing:
            print(f"Skipping tile; missing bands: {missing}")
            continue

        # Read the vegetation indices by their band names.
        indices = {}

        for name in INDEX_NAMES:
            band_number = band_names.index(name) + 1
            values = src.read(band_number, masked=True)
            values = np.ma.filled(values, np.nan).astype(
                np.float32
            )
            values[~np.isfinite(values)] = np.nan

            indices[name] = values

        # Use pixels valid in all three indices.
        valid = np.logical_and.reduce([
            np.isfinite(indices[name])
            for name in INDEX_NAMES
        ])

        if valid.sum() == 0:
            print("Skipping tile; no valid index pixels.")
            continue

        ndvi = indices["NDVI"]
        ndmi = indices["NDMI"]
        evi = indices["EVI"]

        # Descriptive statistics for valid pixels.
        record = {
            "tile": tile_path.name,
            "year": YEAR,
            "valid_pixels": int(valid.sum()),
            "mean_ndvi": float(np.mean(ndvi[valid])),
            "median_ndvi": float(np.median(ndvi[valid])),
            "mean_ndmi": float(np.mean(ndmi[valid])),
            "mean_evi": float(np.mean(evi[valid])),
            "low_ndvi_pixels": int(
                np.sum(valid & (ndvi < NDVI_LOW))
            ),
            "moderate_ndvi_pixels": int(
                np.sum(
                    valid
                    & (ndvi >= NDVI_LOW)
                    & (ndvi < NDVI_HIGH)
                )
            ),
            "high_ndvi_pixels": int(
                np.sum(valid & (ndvi >= NDVI_HIGH))
            )
        }

        records.append(record)

        print(f"Valid pixels: {record['valid_pixels']:,}")
        print(f"Mean NDVI: {record['mean_ndvi']:.4f}")
        print(f"Mean NDMI: {record['mean_ndmi']:.4f}")
        print(f"Mean EVI: {record['mean_evi']:.4f}")

        # ----------------------------------------------------
        # 5. SAVE NDVI VEGETATION-CONDITION MAP
        # ----------------------------------------------------

        ndvi_output = OUTPUT_DIR / (
            tile_path.stem + "_NDVI_baseline.png"
        )

        fig, ax = plt.subplots(figsize=(8, 6))

        image = ax.imshow(
            np.where(valid, ndvi, np.nan),
            cmap="RdYlGn",
            vmin=-1,
            vmax=1
        )

        ax.set_title(
            f"NDVI Baseline - {tile_path.stem}"
        )
        ax.set_xlabel("Pixel column")
        ax.set_ylabel("Pixel row")

        fig.colorbar(image, ax=ax, label="NDVI")
        fig.tight_layout()
        fig.savefig(ndvi_output, dpi=150)
        plt.close(fig)

        print(f"Saved map: {ndvi_output.name}")


# ============================================================
# 6. SAVE SUMMARY TABLE
# ============================================================

if not records:
    raise RuntimeError(
        "No tiles were processed successfully. "
        "Check band descriptions and raster values."
    )

summary = pd.DataFrame(records)

csv_path = OUTPUT_DIR / "vegetation_baseline_2024.csv"
summary.to_csv(csv_path, index=False)

print("\n" + "=" * 60)
print("VEGETATION BASELINE SUMMARY")
print("=" * 60)
print(summary.to_string(index=False))

print(f"\nCSV saved to:\n{csv_path}")


# ============================================================
# 7. SAVE A COMPARISON CHART
# ============================================================

chart_path = OUTPUT_DIR / "vegetation_index_comparison.png"

fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(summary))
width = 0.25

ax.bar(
    x - width,
    summary["mean_ndvi"],
    width,
    label="Mean NDVI"
)
ax.bar(
    x,
    summary["mean_ndmi"],
    width,
    label="Mean NDMI"
)
ax.bar(
    x + width,
    summary["mean_evi"],
    width,
    label="Mean EVI"
)

ax.set_xticks(x)
ax.set_xticklabels(
    summary["tile"],
    rotation=20,
    ha="right"
)
ax.set_ylabel("Mean index value")
ax.set_title(f"Vegetation Index Comparison - {YEAR}")
ax.legend()
fig.tight_layout()
fig.savefig(chart_path, dpi=150)
plt.close(fig)

print(f"Comparison chart saved to:\n{chart_path}")

print("\nCOMPLETED SUCCESSFULLY")
print(
    "Note: vegetation indices describe vegetation properties; "
    "they do not by themselves establish forest loss."
)
