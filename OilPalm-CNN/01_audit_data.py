
from pathlib import Path
import importlib.metadata
import numpy as np
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
PREPARED = ROOT / "prepared_data"
RESULTS = ROOT / "results"

report = []

def log(message=""):
    message = str(message)
    print(message)
    report.append(message)

log("OIL-PALM PROJECT: DATA AUDIT")
log("=" * 60)
log(f"Project folder: {ROOT}")

# 1. Check required Python packages.
log("\n1. PYTHON PACKAGES")
for package in [
    "numpy", "pandas", "rasterio", "torch",
    "scikit-learn", "matplotlib"
]:
    try:
        log(f"{package}: {importlib.metadata.version(package)}")
    except importlib.metadata.PackageNotFoundError:
        log(f"{package}: NOT INSTALLED")

# 2. Inspect raster files without modifying them.
log("\n2. RASTER FILES")
if not DATA.exists():
    log(f"ERROR: Data folder not found: {DATA}")
else:
    rasters = sorted(DATA.glob("*.tif"))
    if not rasters:
        log("WARNING: No .tif files found in data/")
    for path in rasters:
        log(f"\nFile: {path.name}")
        try:
            with rasterio.open(path) as src:
                log(f"Dimensions: {src.width} x {src.height}")
                log(f"Band count: {src.count}")
                log(f"CRS: {src.crs}")
                log(f"Bounds: {src.bounds}")
                log(f"Pixel size/transform: {src.transform}")
                log(f"Band descriptions: {src.descriptions}")
                log(f"Nodata value: {src.nodata}")
                log(f"Data types: {src.dtypes}")
                log(f"File size: {path.stat().st_size:,} bytes")

                # Summarize values in band 1 for the reference raster.
                if "Reference_Labels" in path.name:
                    values, counts = np.unique(
                        src.read(1), return_counts=True
                    )
                    log("Reference band-1 value counts:")
                    for value, count in zip(values, counts):
                        log(f"  {value}: {count:,} pixels")
        except Exception as exc:
            log(f"ERROR reading raster: {exc}")

# 3. Inspect prepared arrays.
log("\n3. PREPARED ARRAYS")
for name in [
    "X_patches_thresholded.npy",
    "y_labels_thresholded.npy",
    "X_patches_supervised.npy",
    "y_labels_supervised.npy"
]:
    path = PREPARED / name
    if path.exists():
        try:
            arr = np.load(path, mmap_mode="r")
            log(f"{name}: shape={arr.shape}, dtype={arr.dtype}")
            if name.startswith("y_labels"):
                values, counts = np.unique(arr, return_counts=True)
                log(f"  Label counts: {dict(zip(values.tolist(), counts.tolist()))}")
        except Exception as exc:
            log(f"ERROR reading {name}: {exc}")
    else:
        log(f"Not found (may be optional): {name}")

# 4. Inspect patch metadata.
log("\n4. PATCH METADATA")
for name in [
    "thresholded_patch_labels.csv",
    "supervised_patch_labels.csv"
]:
    path = PREPARED / name
    if path.exists():
        try:
            df = pd.read_csv(path)
            log(f"{name}: {len(df)} rows")
            log(f"Columns: {df.columns.tolist()}")
            log(df.head(5).to_string(index=False))
        except Exception as exc:
            log(f"ERROR reading {name}: {exc}")
    else:
        log(f"Not found (may be optional): {name}")

# 5. Inventory existing results.
log("\n5. RESULTS FILES")
if RESULTS.exists():
    for path in sorted(RESULTS.iterdir()):
        if path.is_file():
            log(f"{path.name}: {path.stat().st_size:,} bytes")
else:
    log("Results folder not found.")

# 6. Save audit report.
RESULTS.mkdir(parents=True, exist_ok=True)
output = RESULTS / "data_audit.txt"
output.write_text("\n".join(report), encoding="utf-8")
log(f"\nAudit report saved to: {output}")
