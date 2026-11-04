
import rasterio
import numpy as np
from pathlib import Path

data_dir = Path("data")

files = [
    f for f in data_dir.glob("*.tif")
    if "Reference" in f.name or "Labels" in f.name
]

if not files:
    print("Reference TIFF not found in the data folder.")
    print("Copy the downloaded label TIFF into data and run again.")
    raise SystemExit

for file in files:
    print("\nFile:", file.name)

    with rasterio.open(file) as src:
        labels = src.read(1)
        print("CRS:", src.crs)
        print("Dimensions:", src.width, "x", src.height)
        print("Bounds:", src.bounds)
        print("Pixel size:", src.res)
        print("NoData:", src.nodata)

        valid = labels
        if src.nodata is not None:
            valid = labels[labels != src.nodata]

        values, counts = np.unique(valid, return_counts=True)
        print("Pixel values and counts:")
        for value, count in zip(values, counts):
            print(f"  {value}: {count:,}")
