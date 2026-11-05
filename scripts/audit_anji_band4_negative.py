from pathlib import Path
import rasterio
import numpy as np


ROOT = Path(r"D:\Capstone-Project\data\extracted\ANJI\ANJI")

files = list(ROOT.rglob("*_10m.tif"))

total_files = 0
files_with_negative = 0
files_with_zero = 0
total_negative_pixels = 0

global_min = None

print("=" * 70)
print("ANJI 10m Band 4 Negative/Zero Value Audit")
print("=" * 70)

for path in files:
    total_files += 1

    with rasterio.open(path) as src:
        band4 = src.read(4)

    negative_count = np.count_nonzero(band4 < 0)
    zero_count = np.count_nonzero(band4 == 0)
    file_min = int(band4.min())

    if negative_count > 0:
        files_with_negative += 1
        total_negative_pixels += negative_count

        print(
            f"Negative values: {negative_count:4d} | "
            f"Min: {file_min:4d} | "
            f"{path}"
        )

    if zero_count > 0:
        files_with_zero += 1

    if global_min is None or file_min < global_min:
        global_min = file_min


print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)

print(f"Total 10m TIFF files:          {total_files}")
print(f"Files with negative Band 4:   {files_with_negative}")
print(f"Total negative Band 4 pixels: {total_negative_pixels}")
print(f"Files with zero Band 4:       {files_with_zero}")
print(f"Global Band 4 minimum:        {global_min}")