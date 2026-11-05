from pathlib import Path
import rasterio

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

    with rasterio.open(path) as src:
        print(f"Scales:  {src.scales}")
        print(f"Offsets: {src.offsets}")

        for band in range(1, src.count + 1):
            print(f"\nBand {band}:")
            print(f"  Scale:  {src.scales[band - 1]}")
            print(f"  Offset: {src.offsets[band - 1]}")