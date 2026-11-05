import os
import glob
import rasterio
import numpy as np


ROOT = r"D:\Capstone-Project\data\extracted"

DATASETS = [
    "ANJI",
    "ARM",
    "BAMBENW2",
    "ES-IC3XG"
]

band_names = {
    1: "B2",
    2: "B3",
    3: "B4",
    4: "B8 (NIR)"
}


def audit_dataset(dataset_name):

    dataset_root = os.path.join(ROOT, dataset_name)

    files = glob.glob(
        os.path.join(dataset_root, "**", "*_10m.tif"),
        recursive=True
    )

    print()
    print("=" * 70)
    print(f"{dataset_name} — 10m FOUR-BAND QUALITY AUDIT")
    print("=" * 70)

    print(f"Total 10m TIFF files: {len(files)}")

    if not files:
        print("WARNING: No 10m TIFF files found.")
        return

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
            "files_wrong_shape": 0,
            "files_wrong_dtype": 0,
        }

    failed_files = []
    wrong_band_count = []
    wrong_shape_files = []
    wrong_dtype_files = []

    expected_shape = (128, 128)
    expected_dtype = "int16"

    for i, path in enumerate(files, start=1):

        try:

            with rasterio.open(path) as src:

                # Check band count
                if src.count != 4:
                    wrong_band_count.append(path)
                    continue

                # Check dimensions
                if (src.height, src.width) != expected_shape:
                    wrong_shape_files.append(
                        (path, src.height, src.width)
                    )

                # Check dtype
                for band in range(1, 5):

                    if src.dtypes[band - 1] != expected_dtype:
                        wrong_dtype_files.append(
                            (path, band, src.dtypes[band - 1])
                        )

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

        except Exception as e:

            failed_files.append((path, str(e)))

        if i % 250 == 0:
            print(f"Processed {i}/{len(files)} files...")

    # ------------------------------------------------------------
    # STRUCTURAL SUMMARY
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("STRUCTURAL CHECK")
    print("=" * 70)

    print(f"Expected dimensions:        128 x 128")
    print(f"Expected dtype:             int16")
    print(f"Expected bands:             4")

    print(f"Read failures:              {len(failed_files)}")
    print(f"Wrong band count:           {len(wrong_band_count)}")
    print(f"Wrong dimensions:            {len(wrong_shape_files)}")
    print(f"Wrong dtype occurrences:    {len(wrong_dtype_files)}")

    # ------------------------------------------------------------
    # BAND SUMMARY
    # ------------------------------------------------------------

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

    # ------------------------------------------------------------
    # FINAL STATUS
    # ------------------------------------------------------------

    print()
    print("=" * 70)
    print("AUDIT STATUS")
    print("=" * 70)

    if (
        len(failed_files) == 0
        and len(wrong_band_count) == 0
        and len(wrong_shape_files) == 0
        and len(wrong_dtype_files) == 0
    ):
        print("STRUCTURE: PASS")
    else:
        print("STRUCTURE: REVIEW REQUIRED")

    print()
    print("=" * 70)
    print(f"{dataset_name} AUDIT COMPLETE")
    print("=" * 70)


# ================================================================
# RUN ALL DATASETS
# ================================================================

print("=" * 70)
print("ALL DATASETS — 10m FOUR-BAND QUALITY AUDIT")
print("=" * 70)

print(f"Datasets: {', '.join(DATASETS)}")

for dataset in DATASETS:
    audit_dataset(dataset)

print()
print("=" * 70)
print("ALL DATASETS AUDIT COMPLETE")
print("=" * 70)