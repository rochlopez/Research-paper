
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling

DATA_DIR = Path("data")
OUT_DIR = Path("prepared_data")
OUT_DIR.mkdir(exist_ok=True)

REF_FILE = DATA_DIR / "AP_OilPalm_Reference_Labels.tif"
tiles = sorted(DATA_DIR.glob("AP_Sentinel2_2024_Tile_*.tif"))

if not REF_FILE.exists():
    raise FileNotFoundError(f"Missing reference map: {REF_FILE}")
if len(tiles) != 4:
    raise RuntimeError(f"Expected 4 tiles; found {len(tiles)}")

PATCH = 32
X, y, records = [], [], []

with rasterio.open(REF_FILE) as ref:
    ref_data = ref.read(1)

    for tile in tiles:
        print("Processing:", tile.name, flush=True)

        with rasterio.open(tile) as src:
            if src.count != 15:
                raise ValueError(
                    f"{tile.name}: expected 15 bands, found {src.count}"
                )

            labels = np.full(
                (src.height, src.width), 255, dtype=np.uint8
            )

            reproject(
                source=ref_data,
                destination=labels,
                src_transform=ref.transform,
                src_crs=ref.crs,
                src_nodata=ref.nodata,
                dst_transform=src.transform,
                dst_crs=src.crs,
                dst_nodata=255,
                resampling=Resampling.nearest
            )

            image = src.read().astype(np.float32)

            for row in range(0, src.height - PATCH + 1, PATCH):
                for col in range(0, src.width - PATCH + 1, PATCH):
                    patch = image[:, row:row+PATCH, col:col+PATCH]
                    lp = labels[row:row+PATCH, col:col+PATCH]

                    valid = np.isin(lp, [0, 1, 2])
                    if valid.mean() < 0.80:
                        continue
                    if not np.isfinite(patch).all():
                        continue

                    ref_pixels = lp[valid]
                    palm_fraction = np.isin(ref_pixels, [1, 2]).mean()

                    if palm_fraction >= 0.25:
                        label = 1
                    elif palm_fraction <= 0.05:
                        label = 0
                    else:
                        continue

                    X.append(patch)
                    y.append(label)
                    records.append({
                        "tile": tile.name,
                        "row": row,
                        "col": col,
                        "palm_fraction": round(float(palm_fraction), 4),
                        "label": label
                    })

if not y:
    raise RuntimeError("No patches met the selected thresholds.")

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.int64)
df = pd.DataFrame(records)

np.save(OUT_DIR / "X_patches_thresholded.npy", X)
np.save(OUT_DIR / "y_labels_thresholded.npy", y)
df.to_csv(OUT_DIR / "thresholded_patch_labels.csv", index=False)

print("\n--- NEW DATASET SUMMARY ---")
print("Input shape:", X.shape)
print("Label counts:", dict(zip(*np.unique(y, return_counts=True))))
print("Patches per tile:")
print(df.groupby(["tile", "label"]).size().unstack(fill_value=0))
print("Mean oil-palm fraction by label:")
print(df.groupby("label")["palm_fraction"].mean())
print("Saved to:", OUT_DIR.resolve())
