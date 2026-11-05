
from pathlib import Path

import rasterio
import numpy as np

files = {
    "10m_input": Path(
        r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_10m"
        r"\b2b3b4b8\10m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
    ),
    "5m_reference": Path(
        r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_05m"
        r"\b2b3b4b8\05m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"
    ),
}

band_names = ["B2 (blue)", "B3 (green)", "B4 (red)", "B8 (NIR)"]

for label, path in files.items():
    print(f"\n=== {label} ===")
    print("File exists:", path.exists())

    if not path.exists():
        print("STOP: check the path above.")
        continue

    with rasterio.open(path) as src:
        print("Shape (bands, height, width):",
              (src.count, src.height, src.width))
        print("Data type:", src.dtypes)
        print("CRS:", src.crs)

        if src.count != 4:
            print("STOP: expected four bands.")
            continue

        for i, name in enumerate(band_names, start=1):
            raw = src.read(i)
            scaled = raw.astype(np.float32) / 10000.0

            print(
                f"{name}: raw min={raw.min()}, max={raw.max()}, "
                f"scaled min={scaled.min():.5f}, "
                f"max={scaled.max():.5f}, "
                f"mean={scaled.mean():.5f}, "
                f"negative pixels={(raw < 0).sum()}, "
                f"zero pixels={(raw == 0).sum()}"
            )

