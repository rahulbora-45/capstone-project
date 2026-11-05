import rasterio

PATH = (
    r"D:\Capstone-Project\data\extracted\ANJI\ANJI"
    r"\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m"
    r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
)

with rasterio.open(PATH) as src:

    print("=" * 70)
    print("10m ANJI Band 4 Metadata / Tags")
    print("=" * 70)

    print("\nDataset tags:")
    print(src.tags())

    print("\nBand 4 tags:")
    print(src.tags(4))

    print("\nBand 4 scales:")
    print(src.scales)

    print("\nBand 4 offsets:")
    print(src.offsets)

    print("\nBand 4 color interpretation:")
    print(src.colorinterp[3])

    print("\nBand 4 mask flags:")
    print(src.mask_flag_enums[3])