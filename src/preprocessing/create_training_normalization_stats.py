import csv
import json
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_CSV = PROJECT_ROOT / "data" / "prepared" / "splits" / "train.csv"
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted" / "ANJI"
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "normalization"
    / "training_statistics.json"
)


def find_file(filename):
    matches = list(EXTRACTED_DIR.rglob(filename))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one file for {filename}, found {len(matches)}"
        )

    return matches[0]


def calculate_statistics(rows, filename_column):
    channel_min = np.full(4, np.inf, dtype=np.float64)
    channel_max = np.full(4, -np.inf, dtype=np.float64)
    channel_sum = np.zeros(4, dtype=np.float64)
    channel_sum_sq = np.zeros(4, dtype=np.float64)

    total_pixels = 0

    for i, row in enumerate(rows, start=1):
        path = find_file(row[filename_column])

        with rasterio.open(path) as src:
            data = src.read().astype(np.float64)

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
            print(
                f"Processed {i}/{len(rows)} "
                f"training {filename_column.replace('_file', '').upper()} images..."
            )

    channel_mean = channel_sum / total_pixels

    channel_variance = (
        channel_sum_sq / total_pixels
        - np.square(channel_mean)
    )

    channel_std = np.sqrt(
        np.maximum(channel_variance, 0)
    )

    return {
        "minimum": channel_min.tolist(),
        "maximum": channel_max.tolist(),
        "mean": channel_mean.tolist(),
        "std": channel_std.tolist(),
    }


def main():
    print("=" * 70)
    print("CREATING TRAINING NORMALIZATION STATISTICS")
    print("=" * 70)

    with open(SPLIT_CSV, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Training pairs : {len(rows)}")
    print()

    print("Calculating LR statistics...")
    lr_stats = calculate_statistics(rows, "lr_file")

    print()
    print("Calculating HR statistics...")
    hr_stats = calculate_statistics(rows, "hr_file")

    # Shared normalization statistics.
    # We use the average of the LR and HR training statistics
    # because LR and HR represent the same spectral bands and
    # their distributions are closely aligned.
    lr_mean = np.array(lr_stats["mean"])
    hr_mean = np.array(hr_stats["mean"])

    lr_std = np.array(lr_stats["std"])
    hr_std = np.array(hr_stats["std"])

    shared_mean = ((lr_mean + hr_mean) / 2.0).tolist()
    shared_std = ((lr_std + hr_std) / 2.0).tolist()

    statistics = {
        "dataset": "Bengaluru satellite super-resolution dataset",
        "training_pairs": len(rows),
        "channel_order": ["B", "G", "R", "NIR"],
        "normalization": "per-band standardization",
        "formula": "(pixel - mean) / std",
        "statistics_source": "training split only",
        "shared_lr_hr_statistics": True,
        "shared_mean": shared_mean,
        "shared_std": shared_std,
        "lr_statistics": lr_stats,
        "hr_statistics": hr_stats,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(statistics, f, indent=4)

    print()
    print("=" * 70)
    print("SHARED NORMALIZATION STATISTICS")
    print("=" * 70)

    for i, name in enumerate(["B", "G", "R", "NIR"]):
        print(f"{name}:")
        print(f"  Shared mean : {shared_mean[i]:.6f}")
        print(f"  Shared std  : {shared_std[i]:.6f}")

    print()
    print(f"Output file:")
    print(f"  {OUTPUT_FILE}")

    print()
    print("=" * 70)
    print("TRAINING NORMALIZATION STATISTICS: COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()