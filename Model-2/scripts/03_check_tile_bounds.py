
from pathlib import Path
import rasterio

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "OilPalm-CNN" / "data"

for tile_num in range(1, 5):
    path = DATA_DIR / f"AP_Sentinel2_2024_Tile_{tile_num}.tif"

    with rasterio.open(path) as src:
        bounds = src.bounds

        print(f"\nTile {tile_num}")
        print("CRS:", src.crs)
        print("Left longitude:", bounds.left)
        print("Bottom latitude:", bounds.bottom)
        print("Right longitude:", bounds.right)
        print("Top latitude:", bounds.top)
        print("Width x height:", src.width, "x", src.height)
        print("Pixel size:", src.res)

print("\nBounds check complete.")
