import os
import glob
import rasterio
import numpy as np

ROOT = r"D:\Capstone-Project\data\extracted\ANJI\ANJI"

files = glob.glob(
    os.path.join(ROOT, "**", "*_10m.tif"),
    recursive=True
)

print("=" * 70)
print("ANJI 10m — ALL BAND QUALITY AUDIT")
print("=" * 70)

print(f"Total 10m TIFF files: {len(files)}")

band_names = {
    1: "B2",
    2: "B3",
    3: "B4",
    4: "B8 (NIR)"
}

stats = {}

for band in range(1, 5):
    stats[band] = {
        "total_pixels": 0,
        "negative_pixels": 0,
        "zero_pixels": 0,
        "min": None,
        "max": None,
        "files_negative": 0,
        "files_zero": 0,
    }

for i, path in enumerate(files, start=1):

    with rasterio.open(path) as src:

        for band in range(1, 5):

            data = src.read(band)

            negative_count = np.count_nonzero(data < 0)
            zero_count = np.count_nonzero(data == 0)

            band_min = int(data.min())
            band_max = int(data.max())

            s = stats[band]

            s["total_pixels"] += data.size
            s["negative_pixels"] += negative_count
            s["zero_pixels"] += zero_count

            if s["min"] is None or band_min < s["min"]:
                s["min"] = band_min

            if s["max"] is None or band_max > s["max"]:
                s["max"] = band_max

            if negative_count > 0:
                s["files_negative"] += 1

            if zero_count > 0:
                s["files_zero"] += 1

    if i % 250 == 0:
        print(f"Processed {i}/{len(files)} files...")

print()
print("=" * 70)
print("BAND SUMMARY")
print("=" * 70)

for band in range(1, 5):

    s = stats[band]

    total_pixels = s["total_pixels"]

    negative_percentage = (
        s["negative_pixels"] / total_pixels * 100
        if total_pixels > 0 else 0
    )

    zero_percentage = (
        s["zero_pixels"] / total_pixels * 100
        if total_pixels > 0 else 0
    )

    file_negative_percentage = (
        s["files_negative"] / len(files) * 100
        if files else 0
    )

    file_zero_percentage = (
        s["files_zero"] / len(files) * 100
        if files else 0
    )

    print()
    print(f"{band_names[band]}")
    print("-" * 70)

    print(f"Total pixels:                 {total_pixels}")
    print(f"Minimum value:                {s['min']}")
    print(f"Maximum value:                {s['max']}")

    print(
        f"Negative pixels:              "
        f"{s['negative_pixels']} "
        f"({negative_percentage:.6f}%)"
    )

    print(
        f"Files containing negatives:   "
        f"{s['files_negative']} "
        f"({file_negative_percentage:.2f}%)"
    )

    print(
        f"Zero pixels:                  "
        f"{s['zero_pixels']} "
        f"({zero_percentage:.6f}%)"
    )

    print(
        f"Files containing zeros:       "
        f"{s['files_zero']} "
        f"({file_zero_percentage:.2f}%)"
    )

print()
print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
