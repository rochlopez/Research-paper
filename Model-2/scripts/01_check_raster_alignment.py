
from pathlib import Path
import rasterio

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "OilPalm-CNN" / "data"
RESULTS_DIR = ROOT / "OilPalm-CNN" / "results"

print("\nMODEL 2: RASTER ALIGNMENT CHECK\n")

all_ok = True

for tile in range(1, 5):
    image_path = DATA_DIR / f"AP_Sentinel2_2024_Tile_{tile}.tif"
    prediction_path = (
        RESULTS_DIR / f"AP_Sentinel2_2024_Tile_{tile}_prediction.tif"
    )
    probability_path = (
        RESULTS_DIR / f"AP_Sentinel2_2024_Tile_{tile}_probability.tif"
    )

    print(f"\n--- TILE {tile} ---")

    if not image_path.exists():
        print("MISSING IMAGE:", image_path)
        all_ok = False
        continue

    if not prediction_path.exists():
        print("MISSING PREDICTION:", prediction_path)
        all_ok = False
        continue

    with rasterio.open(image_path) as image, \
         rasterio.open(prediction_path) as prediction:

        print("Image shape:", image.height, image.width)
        print("Prediction shape:", prediction.height, prediction.width)
        print("Image CRS:", image.crs)
        print("Prediction CRS:", prediction.crs)
        print("Image transform:", image.transform)
        print("Prediction transform:", prediction.transform)

        aligned = (
            image.shape == prediction.shape
            and image.crs == prediction.crs
            and image.transform == prediction.transform
        )

        print("IMAGE AND PREDICTION ALIGNED:", aligned)

        if not aligned:
            all_ok = False

        values, counts = __import__("numpy").unique(
            prediction.read(1), return_counts=True
        )
        print("Prediction pixel values:", dict(zip(
            values.tolist(), counts.tolist()
        )))

    if probability_path.exists():
        with rasterio.open(probability_path) as probability:
            print("Probability raster shape:", probability.shape)
            print("Probability raster CRS:", probability.crs)
            print("Probability raster bands:", probability.count)
    else:
        print("Probability file not found; continuing without it.")

print("\nOVERALL RESULT:",
      "CHECK PASSED" if all_ok else "CHECK FAILED — REVIEW OUTPUT")
