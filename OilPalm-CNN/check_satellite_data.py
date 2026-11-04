
from pathlib import Path
import rasterio

data_folder = Path(__file__).parent / "data"
files = sorted(data_folder.glob("*.tif"))

print("Satellite files found:", len(files))

for file in files:
    with rasterio.open(file) as image:
        print("\nFile:", file.name)
        print("Bands:", image.count)
        print("Dimensions:", image.width, "x", image.height)
        print("CRS:", image.crs)
        print("Band names:", image.descriptions)

