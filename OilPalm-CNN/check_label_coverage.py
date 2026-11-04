
from pathlib import Path
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

data_dir = Path("data")
ref_file = data_dir / "AP_OilPalm_Reference_Labels.tif"

with rasterio.open(ref_file) as ref:
    reference = ref.read(1)

    for tile in sorted(data_dir.glob("AP_Sentinel2_2024_Tile_*.tif")):
        with rasterio.open(tile) as src:
            aligned = np.full(
                (src.height, src.width), 255, dtype=np.uint8
            )

            reproject(
                source=reference,
                destination=aligned,
                src_transform=ref.transform,
                src_crs=ref.crs,
                src_nodata=ref.nodata,
                dst_transform=src.transform,
                dst_crs=src.crs,
                dst_nodata=255,
                resampling=Resampling.nearest
            )

            print(f"\n{tile.name}")
            values, counts = np.unique(aligned, return_counts=True)
            print("Aligned pixel counts:", dict(zip(values.tolist(), counts.tolist())))

            patch_counts = {}
            total_patches = 0

            for row in range(0, src.height - 31, 32):
                for col in range(0, src.width - 31, 32):
                    p = aligned[row:row+32, col:col+32]
                    valid = np.isin(p, [0, 1, 2])

                    if valid.mean() < 0.80:
                        continue

                    vals, cnts = np.unique(p[valid], return_counts=True)
                    i = np.argmax(cnts)
                    purity = cnts[i] / cnts.sum()

                    if purity >= 0.80:
                        cls = int(vals[i])
                        patch_counts[cls] = patch_counts.get(cls, 0) + 1
                        total_patches += 1

            print("Retained patches by original class:", patch_counts)
            print("Total retained patches:", total_patches)
