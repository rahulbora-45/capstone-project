
import rasterio
import numpy as np

lr_path = (
    r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_10m"
    r"\b2b3b4b8\10m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
)
hr_path = (
    r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_05m"
    r"\b2b3b4b8\05m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"
)

with rasterio.open(lr_path) as lr, rasterio.open(hr_path) as hr:
    nir = lr.read(4)
    negative_positions = np.argwhere(nir < 0)
    zero_positions = np.argwhere(nir == 0)

    print("Negative NIR pixels:", len(negative_positions))
    print("Zero NIR pixels:", len(zero_positions))
    print("Coordinates below use zero-based (row, column) indices.")

    for row, col in negative_positions:
        # Each 10 m pixel corresponds spatially to a 2x2 block
        # in the aligned 5 m reference.
        hr_block = hr.read(
            4,
            window=((row * 2, row * 2 + 2),
                    (col * 2, col * 2 + 2))
        )

        print(f"\n10 m pixel: row={row}, col={col}")
        print("10 m NIR value:", int(nir[row, col]))
        print("Corresponding 5 m NIR block:")
        print(hr_block)
        print(
            "5 m block min/max/mean:",
            int(hr_block.min()),
            int(hr_block.max()),
            float(hr_block.mean())
        )

    print("\nZero-valued NIR pixel positions:")
    for row, col in zero_positions:
        print(f"row={row}, col={col}")
