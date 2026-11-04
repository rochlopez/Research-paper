
from pathlib import Path
import csv
import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "OilPalm-CNN" / "data"
PRED_DIR = ROOT / "OilPalm-CNN" / "results"
OUT_DIR = ROOT / "Model-2" / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Original image band positions (1-based):
# NDVI = band 13, NDMI = band 14, EVI = band 15
INDEX_BANDS = {
    "NDVI": 13,
    "NDMI": 14,
    "EVI": 15,
}

rows = []

for tile_num in range(1, 5):
    image_path = DATA_DIR / f"AP_Sentinel2_2024_Tile_{tile_num}.tif"
    pred_path = PRED_DIR / (
        f"AP_Sentinel2_2024_Tile_{tile_num}_prediction.tif"
    )

    with rasterio.open(image_path) as image_src, \
         rasterio.open(pred_path) as pred_src:

        prediction = pred_src.read(1)

        if (
            image_src.shape != pred_src.shape
            or image_src.crs != pred_src.crs
            or image_src.transform != pred_src.transform
        ):
            raise ValueError(f"Tile {tile_num}: raster grids do not match.")

        # Class 1 means predicted oil palm; exclude 0 and 255.
        palm_mask = prediction == 1
        valid_prediction = prediction != 255

        print(f"\nTile {tile_num}")
        print("Predicted oil-palm pixels:", int(palm_mask.sum()))
        print("Processed pixels:", int(valid_prediction.sum()))

        for index_name, band_number in INDEX_BANDS.items():
            values = image_src.read(band_number).astype(np.float32)
            band_valid = image_src.read_masks(band_number) > 0

            # Exclude non-finite and masked pixels.
            selected = palm_mask & band_valid & np.isfinite(values)
            selected_values = values[selected]

            if selected_values.size == 0:
                mean_value = median_value = p10 = p90 = np.nan
            else:
                mean_value = float(np.mean(selected_values))
                median_value = float(np.median(selected_values))
                p10 = float(np.percentile(selected_values, 10))
                p90 = float(np.percentile(selected_values, 90))

            rows.append({
                "tile": tile_num,
                "index": index_name,
                "predicted_oil_palm_pixels": int(palm_mask.sum()),
                "valid_index_pixels": int(selected_values.size),
                "mean": mean_value,
                "median": median_value,
                "p10": p10,
                "p90": p90,
            })

out_csv = OUT_DIR / "oil_palm_vegetation_baseline.csv"

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\nBaseline saved to:", out_csv)
print("Next: compare these values with monthly observations.")
