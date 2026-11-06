import csv
import json
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLITS_DIR = PROJECT_ROOT / "data" / "prepared" / "splits"
STATS_FILE = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "normalization"
    / "training_statistics.json"
)
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted" / "ANJI"
OUTPUT_DIR = PROJECT_ROOT / "data" / "prepared" / "dataset"


def find_file(filename):
    matches = list(EXTRACTED_DIR.rglob(filename))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one file for {filename}, found {len(matches)}"
        )

    return matches[0]


def normalize(data, mean, std):
    return (
        (data.astype(np.float32) - mean[:, None, None])
        / std[:, None, None]
    ).astype(np.float32)


def process_split(split_name, mean, std):
    split_csv = SPLITS_DIR / f"{split_name}.csv"

    with open(split_csv, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    lr_output_dir = OUTPUT_DIR / split_name / "lr"
    hr_output_dir = OUTPUT_DIR / split_name / "hr"

    lr_output_dir.mkdir(parents=True, exist_ok=True)
    hr_output_dir.mkdir(parents=True, exist_ok=True)

    successful = 0
    failed = 0

    for i, row in enumerate(rows, start=1):
        try:
            lr_path = find_file(row["lr_file"])
            hr_path = find_file(row["hr_file"])

            with rasterio.open(lr_path) as src:
                lr_data = src.read()
                lr_profile = src.profile.copy()

            with rasterio.open(hr_path) as src:
                hr_data = src.read()
                hr_profile = src.profile.copy()

            if lr_data.shape != (4, 128, 128):
                raise ValueError(
                    f"Unexpected LR shape: {lr_data.shape}"
                )

            if hr_data.shape != (4, 256, 256):
                raise ValueError(
                    f"Unexpected HR shape: {hr_data.shape}"
                )

            lr_normalized = normalize(lr_data, mean, std)
            hr_normalized = normalize(hr_data, mean, std)

            lr_profile.update(
                dtype="float32",
                count=4,
                compress="deflate"
            )

            hr_profile.update(
                dtype="float32",
                count=4,
                compress="deflate"
            )

            lr_output_path = lr_output_dir / row["lr_file"]
            hr_output_path = hr_output_dir / row["hr_file"]

            with rasterio.open(lr_output_path, "w", **lr_profile) as dst:
                dst.write(lr_normalized)

            with rasterio.open(hr_output_path, "w", **hr_profile) as dst:
                dst.write(hr_normalized)

            successful += 1

        except Exception as e:
            failed += 1
            print()
            print(f"FAILED: {row['lr_file']}")
            print(f"Reason: {e}")

        if i % 250 == 0 or i == len(rows):
            print(
                f"Processed {i}/{len(rows)} {split_name} pairs..."
            )

    return len(rows), successful, failed


def main():
    print("=" * 70)
    print("CREATING MODEL-READY DATASET")
    print("=" * 70)

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)

    mean = np.array(stats["shared_mean"], dtype=np.float32)
    std = np.array(stats["shared_std"], dtype=np.float32)

    print()
    print("Normalization:")
    print("  Method : per-band standardization")
    print("  Source : training split only")
    print("  Shared : LR and HR")
    print("  Clipping: None")

    print()
    print("Shared mean:")
    print(mean)

    print("Shared std:")
    print(std)

    total_expected = 0
    total_successful = 0
    total_failed = 0

    print()

    for split_name in ["train", "val", "test"]:
        print("-" * 70)
        print(f"Processing {split_name.upper()}")

        expected, successful, failed = process_split(
            split_name,
            mean,
            std
        )

        total_expected += expected
        total_successful += successful
        total_failed += failed

        print(f"{split_name} expected   : {expected}")
        print(f"{split_name} successful : {successful}")
        print(f"{split_name} failed     : {failed}")

    print()
    print("=" * 70)
    print("MODEL-READY DATASET CREATION COMPLETE")
    print("=" * 70)
    print(f"Expected pairs   : {total_expected}")
    print(f"Successful pairs : {total_successful}")
    print(f"Failed pairs     : {total_failed}")

    if total_failed == 0 and total_successful == total_expected:
        print()
        print("MODEL-READY DATASET CREATION: PASS")
    else:
        print()
        print("MODEL-READY DATASET CREATION: FAIL")


if __name__ == "__main__":
    main()