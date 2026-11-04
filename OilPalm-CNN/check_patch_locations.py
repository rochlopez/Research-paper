
import numpy as np
import rasterio
from pathlib import Path

# Project folders
data_dir = Path("data")
patch_dir = Path("prepared_data")

# Load patch metadata
patch_sources = np.load(
    patch_dir / "patch_sources.npy",
    allow_pickle=True
)

print("Total patches:", len(patch_sources))
print("\nPatches per source tile:")

for name, count in zip(
    *np.unique(patch_sources, return_counts=True)
):
    print(name, ":", count)

print("\nChecking TIFF geographic information...")

for name in np.unique(patch_sources):
    matches = list(data_dir.rglob(str(name)))

    if not matches:
        print("File not found:", name)
        continue

    with rasterio.open(matches[0]) as src:
        print("\nFile:", name)
        print("CRS:", src.crs)
        print("Bounds:", src.bounds)
        print("Dimensions:", src.width, "x", src.height)
        print("Transform:", src.transform)
