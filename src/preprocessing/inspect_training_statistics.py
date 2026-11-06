import csv
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_CSV = PROJECT_ROOT / "data" / "prepared" / "splits" / "train.csv"
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted" / "ANJI"


def find_file(filename):
    matches = list(EXTRACTED_DIR.rglob(filename))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one file for {filename}, found {len(matches)}"
        )

    return matches[0]


def main():
    print("=" * 70)
    print("TRAINING DATA STATISTICS")
    print("=" * 70)

    with open(SPLIT_CSV, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Training LR images : {len(rows)}")
    print()

    channel_min = np.full(4, np.inf, dtype=np.float64)
    channel_max = np.full(4, -np.inf, dtype=np.float64)
    channel_sum = np.zeros(4, dtype=np.float64)
    channel_sum_sq = np.zeros(4, dtype=np.float64)

    total_pixels = 0

    for i, row in enumerate(rows, start=1):
        path = find_file(row["lr_file"])

        with rasterio.open(path) as src:
            data = src.read().astype(np.float64)

        # data shape: (4, 128, 128)
        pixels = data.reshape(4, -1)

        channel_min = np.minimum(
            channel_min,
            pixels.min(axis=1)
        )

        channel_max = np.maximum(
            channel_max,
            pixels.max(axis=1)
        )

        channel_sum += pixels.sum(axis=1)
        channel_sum_sq += np.square(pixels).sum(axis=1)

        total_pixels += pixels.shape[1]

        if i % 250 == 0 or i == len(rows):
            print(f"Processed {i}/{len(rows)} training images...")

    channel_mean = channel_sum / total_pixels

    channel_variance = (
        channel_sum_sq / total_pixels
        - np.square(channel_mean)
    )

    channel_std = np.sqrt(
        np.maximum(channel_variance, 0)
    )

    print()
    print("=" * 70)
    print("TRAINING LR STATISTICS")
    print("=" * 70)

    print(f"Total pixels per channel : {total_pixels}")

    print()
    print("Channel order: B, G, R, NIR")
    print()

    for i, name in enumerate(["B", "G", "R", "NIR"]):
        print(f"{name}:")
        print(f"  Minimum : {channel_min[i]:.6f}")
        print(f"  Maximum : {channel_max[i]:.6f}")
        print(f"  Mean    : {channel_mean[i]:.6f}")
        print(f"  Std     : {channel_std[i]:.6f}")

    print()
    print("=" * 70)
    print("TRAINING STATISTICS INSPECTION: COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()