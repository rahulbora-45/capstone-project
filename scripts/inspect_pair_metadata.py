
from pathlib import Path
import rasterio

FILES = {
    "10m_input": Path(r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"),
    "5m_reference": Path(r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_05m\b2b3b4b8\05m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"),
}

for label, path in FILES.items():
    print(f"\n{'=' * 65}")
    print(f"{label}: {path}")

    if not path.is_file():
        print("ERROR: File not found. Verify the actual path.")
        continue

    with rasterio.open(path) as src:
        print(f"CRS:             {src.crs}")
        print(f"Dimensions:      {src.width} x {src.height}")
        print(f"Band count:      {src.count}")
        print(f"Data types:      {src.dtypes}")
        print(f"Transform:       {src.transform}")
        print(f"Bounds:          {src.bounds}")
        print(f"Resolution:      {src.res}")
        print(f"NoData value:    {src.nodata}")
        print(f"Band descriptions: {src.descriptions}")
        print(f"Band indexes:    {src.indexes}")
        print(f"Dataset tags:    {src.tags()}")
        print(f"Band 1 tags:     {src.tags(1)}")
        print(f"Valid data mask: {src.mask_flag_enums}")
