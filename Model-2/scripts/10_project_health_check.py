
from pathlib import Path
import pandas as pd

# Project folders
MODEL2_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = MODEL2_DIR.parent
RESULTS = MODEL2_DIR / "results"
TIMESERIES = MODEL2_DIR / "data" / "timeseries"
CNN_DIR = PROJECT_DIR / "OilPalm-CNN"
CNN_RESULTS = CNN_DIR / "results"
CNN_DATA = CNN_DIR / "data"

print("=" * 60)
print("OIL PALM PROJECT: HEALTH CHECK")
print("=" * 60)

def report(label, path):
    print(f"{'OK' if path.exists() else 'MISSING'} | {label}")
    print(f"       {path}")

print("\n1. MODEL 1")
report("Trained CNN model", CNN_RESULTS / "supervised_cnn_final.pth")
report("Reference labels", CNN_DATA / "AP_OilPalm_Reference_Labels.tif")

for tile in range(1, 5):
    report(f"Tile {tile} prediction",
           CNN_RESULTS / f"AP_Sentinel2_2024_Tile_{tile}_prediction.tif")
    report(f"Tile {tile} probability",
           CNN_RESULTS / f"AP_Sentinel2_2024_Tile_{tile}_probability.tif")

print("\n2. MODEL 2 TABLES AND FIGURES")
files = [
    "oil_palm_vegetation_baseline.csv",
    "monthly_oil_palm_statistics.csv",
    "comparison_2024_vs_2026.csv",
    "change_summary_by_tile.csv",
    "change_summary_by_tile_final.csv",
    "mean_change_by_tile.png",
    "change_direction_by_tile.png",
]

for name in files:
    report(name, RESULTS / name)

print("\n3. MONTHLY TIFF INVENTORY")
if TIMESERIES.exists():
    tiffs = sorted(TIMESERIES.glob("*.tif"))
    print(f"Monthly TIFF files found: {len(tiffs)}")
    for year in (2024, 2026):
        count = sum(str(year) in p.name for p in tiffs)
        print(f"  {year}: {count} files")
    print("Sample filenames:")
    for p in tiffs[:8]:
        print(" ", p.name)
else:
    print("MISSING | Timeseries folder:", TIMESERIES)

print("\n4. SUMMARY DATA CHECK")
csv_path = RESULTS / "comparison_2024_vs_2026.csv"

if csv_path.exists():
    df = pd.read_csv(csv_path)
    print("Comparison rows:", len(df))
    print("Columns:", ", ".join(df.columns))

    if "status" in df.columns:
        print("\nComparison status counts:")
        print(df["status"].value_counts(dropna=False).to_string())

summary_path = RESULTS / "change_summary_by_tile.csv"
if summary_path.exists():
    summary = pd.read_csv(summary_path)
    print("\nChange-summary rows:", len(summary))
    print(summary.to_string(index=False))

print("\nHealth check finished. No files were changed.")
