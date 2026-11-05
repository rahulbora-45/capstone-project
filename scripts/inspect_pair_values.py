
from pathlib import Path

import numpy as np
import rasterio

FILES = {
    "10m_input": Path(
        r"D:\Dataset\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_10m"
        r"\b2b3b4b8\10m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
    ),
    "5m_reference": Path(
        r"D:\Dataset\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_05m"
        r"\b2b3b4b8\05m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"
    ),
}

for name, path in FILES.items():
    print(f"\n{'=' * 55}\n{name}")

    if not path.is_file():
        print(f"File not found: {path}")
        continue

    with rasterio.open(path) as src:
        print("Band order: not yet confirmed from descriptions")
        print("Dataset mask flags:", src.mask_flag_enums)

        for band in range(1, src.count + 1):
            data = src.read(band)
            mask = src.read_masks(band)

            print(f"\nBand {band}")
            print("  Min:", int(data.min()))
            print("  Max:", int(data.max()))
            print("  Mean:", round(float(data.mean()), 3))
            print("  Std:", round(float(data.std()), 3))
            print("  Unique values (first 15):",
                  np.unique(data)[:15].tolist())
            print("  Mask-valid pixels:",
                  int(np.count_nonzero(mask > 0)), "/", mask.size)
            print("  Zero-valued pixels:",
                  int(np.count_nonzero(data == 0)))
