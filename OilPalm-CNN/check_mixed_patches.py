
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

data_dir = Path("data")
reference_file = data_dir / "AP_OilPalm_Reference_Labels.tif"

with rasterio.open(reference_file) as ref:
    reference = ref.read(1)

    for tile in sorted(data_dir.glob("AP_Sentinel2_2024_Tile_*.tif")):
        with rasterio.open(tile) as src:
            labels = np.full(
                (src.height, src.width), 255, dtype=np.uint8
            )

            reproject(
                source=reference,
                destination=labels,
                src_transform=ref.transform,
                src_crs=ref.crs,
                src_nodata=ref.nodata,
                dst_transform=src.transform,
                dst_crs=src.crs,
                dst_nodata=255,
                resampling=Resampling.nearest
            )

            counts = {
                "total": 0,
                "contains_class_1": 0,
                "contains_class_2": 0,
                "palm_majority": 0,
                "palm_at_least_25_percent": 0,
                "palm_at_least_10_percent": 0
            }

            for row in range(0, src.height - 31, 32):
                for col in range(0, src.width - 31, 32):
                    p = labels[row:row + 32, col:col + 32]
                    valid = np.isin(p, [0, 1, 2])

                    if valid.mean() < 0.80:
                        continue

                    p = p[valid]
                    counts["total"] += 1

                    palm_fraction = np.isin(p, [1, 2]).mean()

                    if np.any(p == 1):
                        counts["contains_class_1"] += 1
                    if np.any(p == 2):
                        counts["contains_class_2"] += 1
                    if palm_fraction > 0.50:
                        counts["palm_majority"] += 1
                    if palm_fraction >= 0.25:
                        counts["palm_at_least_25_percent"] += 1
                    if palm_fraction >= 0.10:
                        counts["palm_at_least_10_percent"] += 1

            print(f"\n{tile.name}")
            for key, value in counts.items():
                print(f"{key}: {value}")
