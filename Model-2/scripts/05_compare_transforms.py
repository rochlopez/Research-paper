
from pathlib import Path
import rasterio

ROOT = Path(__file__).resolve().parents[2]

original_dir = ROOT / "OilPalm-CNN" / "data"
monthly_dir = ROOT / "Model-2" / "data" / "timeseries"

for tile in range(1, 5):
    original_path = original_dir / f"AP_Sentinel2_2024_Tile_{tile}.tif"
    monthly_path = monthly_dir / f"M2_Tile_{tile}_2024_01.tif"

    print(f"\n{'=' * 55}")
    print(f"TILE {tile}")

    with rasterio.open(original_path) as original, \
         rasterio.open(monthly_path) as monthly:

        print("Original dimensions:", original.width, original.height)
        print("Monthly dimensions:", monthly.width, monthly.height)
        print("Same CRS:", original.crs == monthly.crs)
        print("Exact transform match:",
              original.transform == monthly.transform)

        differences = [
            abs(a - b)
            for a, b in zip(original.transform, monthly.transform)
        ]
        print("Transform differences:", differences)
        print("Maximum difference:", max(differences))

        print("Bounds differences:")
        print("Left:", original.bounds.left - monthly.bounds.left)
        print("Bottom:", original.bounds.bottom - monthly.bounds.bottom)
        print("Right:", original.bounds.right - monthly.bounds.right)
        print("Top:", original.bounds.top - monthly.bounds.top)

        same_dimensions = (
            original.width == monthly.width
            and original.height == monthly.height
        )
        same_crs = original.crs == monthly.crs
        close_transform = max(differences) < 1e-10

        print(
            "Grid matches within tolerance:",
            same_dimensions and same_crs and close_transform
        )
