
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import reproject, Resampling

DATA_DIR = Path("data")
OUT_DIR = Path("prepared_data")
OUT_DIR.mkdir(exist_ok=True)

reference_file = DATA_DIR / "AP_OilPalm_Reference_Labels.tif"
tile_files = sorted(DATA_DIR.glob("AP_Sentinel2_2024_Tile_*.tif"))

print("Starting supervised dataset preparation...", flush=True)

if not reference_file.exists():
    raise FileNotFoundError(f"Reference map not found: {reference_file.resolve()}")

if len(tile_files) != 4:
    raise RuntimeError(
        f"Expected 4 satellite tiles but found {len(tile_files)} in "
        f"{DATA_DIR.resolve()}"
    )

X, y, records = [], [], []

with rasterio.open(reference_file) as ref:
    reference = ref.read(1)

    for tile_path in tile_files:
        print(f"Processing {tile_path.name}...", flush=True)

        with rasterio.open(tile_path) as src:
            if src.count != 15:
                raise ValueError(
                    f"{tile_path.name} contains {src.count} bands; expected 15."
                )

            labels = np.full(
                (src.height, src.width), 255, dtype=np.uint8
            )

            reproject(
                source=reference,
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

            for row in range(0, src.height - 31, 32):
                for col in range(0, src.width - 31, 32):
                    patch = image[:, row:row + 32, col:col + 32]
                    lp = labels[row:row + 32, col:col + 32]

                    valid = np.isin(lp, [0, 1, 2])
                    if valid.mean() < 0.80:
                        continue

                    values, counts = np.unique(lp[valid], return_counts=True)
                    idx = np.argmax(counts)
                    original_class = int(values[idx])
                    purity = float(counts[idx] / counts.sum())

                    if purity < 0.80 or not np.isfinite(patch).all():
                        continue

                    # 0 = other land cover; 1 = either oil-palm class
                    binary_label = 0 if original_class == 0 else 1

                    X.append(patch)
                    y.append(binary_label)
                    records.append({
                        "tile": tile_path.name,
                        "row": row,
                        "col": col,
                        "reference_class": original_class,
                        "binary_label": binary_label,
                        "label_purity": round(purity, 4)
                    })

X = np.asarray(X, dtype=np.float32)
y = np.asarray(y, dtype=np.int64)

if len(y) == 0:
    raise RuntimeError(
        "No patches passed the label checks. We need to inspect alignment "
        "and reference-map coverage before training."
    )

np.save(OUT_DIR / "X_patches_supervised.npy", X)
np.save(OUT_DIR / "y_labels_supervised.npy", y)
pd.DataFrame(records).to_csv(
    OUT_DIR / "supervised_patch_labels.csv", index=False
)

print("\n--- DATASET SUMMARY ---")
print("Patch shape:", X.shape)
print("Expected format: (patch_count, 15, 32, 32)")
print("Binary label counts:", dict(zip(*np.unique(y, return_counts=True))))
print("Original class counts:")
print(pd.Series([r["reference_class"] for r in records]).value_counts().sort_index())
print("Saved dataset to:", OUT_DIR.resolve())
