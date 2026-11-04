
from pathlib import Path
import numpy as np
import rasterio
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PREPARED = ROOT / "prepared_data"
RESULTS = ROOT / "results"

reference_path = DATA / "AP_OilPalm_Reference_Labels.tif"

print("\n=== REFERENCE RASTER CHECK ===")

with rasterio.open(reference_path) as src:
    labels = src.read(1)
    print("Shape:", labels.shape)
    print("CRS:", src.crs)
    print("Bounds:", src.bounds)
    print("Transform:", src.transform)
    print("Nodata:", src.nodata)
    print("Unique values and counts:")
    values, counts = np.unique(labels, return_counts=True)
    for value, count in zip(values, counts):
        print(f"  {value}: {count:,} pixels")

print("\n=== LABEL MAPPING CHECK ===")

metadata_path = PREPARED / "thresholded_patch_labels.csv"

if metadata_path.exists():
    df = pd.read_csv(metadata_path)
    print("Patch count:", len(df))
    print("\nLabels by tile:")
    print(pd.crosstab(df["tile"], df["label"]))
    print("\nPalm fraction by label:")
    print(df.groupby("label")["palm_fraction"].agg(
        ["count", "min", "mean", "max"]
    ))
else:
    print("Thresholded metadata CSV not found.")

print("\n=== MODEL EVALUATION ===")

evaluation_path = RESULTS / "supervised_cnn_tile_evaluation.csv"

if evaluation_path.exists():
    print(pd.read_csv(evaluation_path).to_string(index=False))
else:
    print("Evaluation CSV not found.")

print("\n=== PREDICTION RASTER CHECK ===")

for path in sorted(RESULTS.glob("*_prediction.tif")):
    with rasterio.open(path) as src:
        arr = src.read(1)
        values, counts = np.unique(arr, return_counts=True)
        print(f"\n{path.name}")
        print("Shape:", arr.shape)
        print("CRS:", src.crs)
        print("Nodata:", src.nodata)
        print("Class counts:", dict(zip(values.tolist(),
                                        counts.tolist())))
