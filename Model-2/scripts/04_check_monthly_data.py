
from pathlib import Path
import re
import rasterio

# Project folders
ROOT = Path(__file__).resolve().parents[2]
MONTHLY_DIR = ROOT / "Model-2" / "data" / "timeseries"
ORIGINAL_DIR = ROOT / "OilPalm-CNN" / "data"

print("=" * 65)
print("MODEL 2: MONTHLY DATA VALIDATION")
print("=" * 65)

if not MONTHLY_DIR.exists():
    raise FileNotFoundError(
        f"Monthly folder not found: {MONTHLY_DIR}"
    )

files = sorted(MONTHLY_DIR.glob("*.tif"))
print(f"\nMonthly TIFF files found: {len(files)}")

if not files:
    raise RuntimeError(
        "No TIFF files found. Copy the extracted files "
        "into Model-2/data/timeseries/ first."
    )

# Expected filenames: M2_Tile_1_2024_01.tif
pattern = re.compile(
    r"M2_Tile_([1-4])_(2024|2026)_(\d{2})\.tif$",
    re.IGNORECASE
)

found = set()
errors = []

expected_bands = ["NDVI", "NDMI", "EVI", "OBS_COUNT"]

for path in files:
    match = pattern.match(path.name)

    if not match:
        print(f"\nFilename needs checking: {path.name}")
        continue

    tile, year, month = match.groups()
    tile, year, month = int(tile), int(year), int(month)

    found.add((tile, year, month))

    if not (1 <= month <= 12):
        errors.append(f"Invalid month in {path.name}")
        continue

    try:
        with rasterio.open(path) as src:
            descriptions = list(src.descriptions)

            print(f"\n{path.name}")
            print(f"  Size: {src.width} x {src.height}")
            print(f"  CRS: {src.crs}")
            print(f"  Bands: {src.count}")
            print(f"  Band names: {descriptions}")
            print(f"  Transform: {src.transform}")

            if src.count != 4:
                errors.append(
                    f"{path.name}: expected 4 bands, "
                    f"found {src.count}"
                )

            if src.crs is None:
                errors.append(
                    f"{path.name}: missing CRS"
                )

            if descriptions != expected_bands:
                print(
                    "  NOTE: Band descriptions differ from "
                    "the expected names/order."
                )

            original_path = (
                ORIGINAL_DIR /
                f"AP_Sentinel2_2024_Tile_{tile}.tif"
            )

            if original_path.exists():
                with rasterio.open(original_path) as original:
                    same_grid = (
                        src.width == original.width
                        and src.height == original.height
                        and src.crs == original.crs
                        and src.transform == original.transform
                    )

                    print(
                        "  Exact grid match to original:",
                        same_grid
                    )

                    if not same_grid:
                        print(
                            "  WARNING: alignment must be "
                            "checked before pixel-by-pixel analysis."
                        )

    except Exception as exc:
        errors.append(f"{path.name}: {exc}")

# Check the expected number of monthly files
expected = set()

for tile in range(1, 5):
    for month in range(1, 13):
        expected.add((tile, 2024, month))

    for month in range(1, 11):
        expected.add((tile, 2026, month))

missing = sorted(expected - found)

print("\n" + "=" * 65)
print("SUMMARY")
print("=" * 65)
print("Expected files: 88")
print("Files found:   ", len(files))
print("Expected month/tile combinations missing:", len(missing))

if missing:
    for tile, year, month in missing:
        print(f"  Missing: Tile {tile}, {year}-{month:02d}")

if errors:
    print("\nProblems detected:")
    for error in errors:
        print(" -", error)
else:
    print("\nNo basic file-reading errors detected.")

print("\nValidation complete.")
