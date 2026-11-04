
from pathlib import Path
import csv
import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "Model-2" / "data" / "timeseries"
PRED_DIR = ROOT / "OilPalm-CNN" / "results"
OUT_DIR = ROOT / "Model-2" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

INDEX_BANDS = {
    "NDVI": 1,
    "NDMI": 2,
    "EVI": 3,
}

output_csv = OUT_DIR / "monthly_oil_palm_statistics.csv"
rows = []

for tile in range(1, 5):
    pred_path = PRED_DIR / f"AP_Sentinel2_2024_Tile_{tile}_prediction.tif"

    if not pred_path.exists():
        print(f"Missing prediction raster: {pred_path}")
        continue

    with rasterio.open(pred_path) as pred_src:
        prediction = pred_src.read(1)
        pred_transform = pred_src.transform
        pred_crs = pred_src.crs
        pred_shape = prediction.shape

    # Class 1 represents predicted oil palm; 255 is unprocessed.
    oil_palm_mask = prediction == 1
    print(f"\nTile {tile}: {oil_palm_mask.sum()} predicted oil-palm pixels")

    for year in (2024, 2026):
        for month in range(1, 13 if year == 2024 else 11):
            monthly_path = DATA_DIR / f"M2_Tile_{tile}_{year}_{month:02d}.tif"

            if not monthly_path.exists():
                print(f"Missing: {monthly_path.name}")
                for index_name in INDEX_BANDS:
                    rows.append({
                        "tile": tile,
                        "year": year,
                        "month": month,
                        "index": index_name,
                        "predicted_oil_palm_pixels": int(oil_palm_mask.sum()),
                        "valid_pixels": 0,
                        "mean": "",
                        "median": "",
                        "p10": "",
                        "p90": "",
                        "mean_obs_count": "",
                        "status": "MISSING_FILE",
                    })
                continue

            with rasterio.open(monthly_path) as src:
                if (
                    src.shape != pred_shape
                    or src.crs != pred_crs
                    or max(abs(a - b) for a, b in zip(src.transform, pred_transform)) > 1e-10
                ):
                    raise ValueError(
                        f"Grid mismatch: {monthly_path.name}. Stop before analysis."
                    )

                for index_name, band_number in INDEX_BANDS.items():
                    index_data = src.read(band_number).astype(np.float32)
                    obs_count = src.read(4).astype(np.float32)

                    valid = (
                        oil_palm_mask
                        & np.isfinite(index_data)
                        & (index_data >= -1)
                        & (index_data <= 1)
                        & np.isfinite(obs_count)
                        & (obs_count >= 1)
                    )

                    values = index_data[valid]
                    observations = obs_count[valid]

                    if values.size == 0:
                        stats = {
                            "valid_pixels": 0,
                            "mean": "",
                            "median": "",
                            "p10": "",
                            "p90": "",
                            "mean_obs_count": "",
                            "status": "NO_VALID_PIXELS",
                        }
                    else:
                        stats = {
                            "valid_pixels": int(values.size),
                            "mean": float(np.mean(values)),
                            "median": float(np.median(values)),
                            "p10": float(np.percentile(values, 10)),
                            "p90": float(np.percentile(values, 90)),
                            "mean_obs_count": float(np.mean(observations)),
                            "status": "OK",
                        }

                    rows.append({
                        "tile": tile,
                        "year": year,
                        "month": month,
                        "index": index_name,
                        "predicted_oil_palm_pixels": int(oil_palm_mask.sum()),
                        **stats,
                    })

                    print(
                        f"Tile {tile} | {year}-{month:02d} | {index_name} "
                        f"| valid={stats['valid_pixels']} "
                        f"| mean={stats['mean']}"
                    )

fields = [
    "tile", "year", "month", "index",
    "predicted_oil_palm_pixels", "valid_pixels",
    "mean", "median", "p10", "p90",
    "mean_obs_count", "status",
]

with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print("\nAnalysis complete.")
print("Saved:", output_csv)
print("Rows written:", len(rows))
