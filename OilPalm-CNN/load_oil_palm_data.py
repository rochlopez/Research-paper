
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio


# ==========================================
# 1. SET PROJECT PATHS
# ==========================================

# Folder containing this Python file
PROJECT_DIR = Path(__file__).resolve().parent

# Satellite images are inside the data folder
DATA_DIR = PROJECT_DIR / "data"

# CSV file is directly inside OilPalm-CNN
CSV_FILE = PROJECT_DIR / "oil_palm_mandal_data.csv"


# ==========================================
# 2. LOAD OIL PALM MANDAL DATA
# ==========================================

print("=" * 60)
print("OIL PALM DATA LOADING")
print("=" * 60)

if CSV_FILE.exists():
    df = pd.read_csv(CSV_FILE)

    print("\nCSV loaded successfully!")
    print("CSV file:", CSV_FILE.name)
    print("Number of rows:", df.shape[0])
    print("Number of columns:", df.shape[1])

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five rows:")
    print(df.head())

    print("\nMissing values in each column:")
    print(df.isnull().sum())

else:
    print("\nERROR: CSV file not found!")
    print("Expected location:", CSV_FILE)


# ==========================================
# 3. FIND SATELLITE TIFF FILES
# ==========================================

print("\n" + "=" * 60)
print("SATELLITE IMAGE INSPECTION")
print("=" * 60)

tif_files = sorted(DATA_DIR.glob("*.tif"))

if not tif_files:
    print("\nERROR: No TIFF files found!")
    print("Expected folder:", DATA_DIR)

else:
    print("\nNumber of satellite images:", len(tif_files))

    for tif_file in tif_files:

        print("\n" + "-" * 60)
        print("File:", tif_file.name)

        try:
            with rasterio.open(tif_file) as src:

                print("Number of bands:", src.count)
                print(
                    "Image dimensions:",
                    src.width,
                    "x",
                    src.height
                )
                print("Coordinate system:", src.crs)
                print("No-data value:", src.nodata)
                print("Band names:", src.descriptions)

                # Check whether this image has all 15 expected bands
                if src.count != 15:
                    print(
                        "WARNING: Expected 15 bands, "
                        "but found", src.count
                    )
                    continue

                # Read vegetation indices
                # Band 13 = NDVI
                # Band 14 = NDMI
                ndvi = src.read(13, masked=True).astype("float32")
                ndmi = src.read(14, masked=True).astype("float32")
                evi = src.read(15, masked=True).astype("float32")

                print("\nVegetation index statistics:")

                for name, band in [
                    ("NDVI", ndvi),
                    ("NDMI", ndmi),
                    ("EVI", evi)
                ]:
                    valid_values = band.compressed()
                    valid_values = valid_values[
                        np.isfinite(valid_values)
                    ]

                    if valid_values.size > 0:
                        print(
                            f"{name}: "
                            f"min={valid_values.min():.4f}, "
                            f"max={valid_values.max():.4f}, "
                            f"mean={valid_values.mean():.4f}"
                        )
                    else:
                        print(f"{name}: No valid pixel values")

        except Exception as error:
            print("Could not read this file:", error)


# ==========================================
# 4. FINISH
# ==========================================

print("\n" + "=" * 60)
print("DATA LOADING AND INSPECTION COMPLETED!")
print("=" * 60)
