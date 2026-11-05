from pathlib import Path
import rasterio
import numpy as np

PATH = Path(
    r"D:\Capstone-Project\data\extracted\ANJI\ANJI"
    r"\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m"
    r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
)

with rasterio.open(PATH) as src:
    data = src.read(4)

    negative_positions = np.argwhere(data < 0)

    print("=" * 70)
    print("10m ANJI Band 4 Negative Pixel Neighborhoods")
    print("=" * 70)

    for row, col in negative_positions:

        r1 = max(0, row - 1)
        r2 = min(data.shape[0], row + 2)

        c1 = max(0, col - 1)
        c2 = min(data.shape[1], col + 2)

        neighborhood = data[r1:r2, c1:c2]

        print(f"\nNegative pixel: row={row}, col={col}")
        print(f"Value: {int(data[row, col])}")
        print("3x3 neighborhood:")
        print(neighborhood)

        print(
            "Neighborhood min/max/mean:",
            int(neighborhood.min()),
            int(neighborhood.max()),
            float(neighborhood.mean())
        )