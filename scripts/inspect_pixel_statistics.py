from pathlib import Path
import rasterio
import numpy as np

FILES = {
    "10m_input": Path(
        r"D:\Capstone-Project\data\extracted\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
    ),
    "5m_reference": Path(
        r"D:\Capstone-Project\data\extracted\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_05m\b2b3b4b8\05m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"
    ),
}

for label, path in FILES.items():
    print("\n" + "=" * 65)
    print(f"{label}: {path}")

    if not path.is_file():
        print("ERROR: File not found.")
        continue

    with rasterio.open(path) as src:
        print(f"Dimensions: {src.width} x {src.height}")
        print(f"Band count: {src.count}")
        print(f"Data types: {src.dtypes}")
        print(f"NoData:     {src.nodata}")

        for band in range(1, src.count + 1):
            data = src.read(band)

            print(f"\n--- Band {band} ---")
            print(f"Min:              {data.min()}")
            print(f"Max:              {data.max()}")
            print(f"Mean:             {data.mean():.4f}")
            print(f"Median:           {np.median(data):.4f}")
            print(f"Std:              {data.std():.4f}")
            print(f"Negative pixels:  {(data < 0).sum()}")
            print(f"Zero pixels:      {(data == 0).sum()}")
            print(f"Positive pixels:  {(data > 0).sum()}")
            print(f"Total pixels:     {data.size}")
            print(
                f"Negative %:       {(data < 0).sum() / data.size * 100:.4f}%"
            )