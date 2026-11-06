import csv
import json
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLIT_CSV = PROJECT_ROOT / "data" / "prepared" / "splits" / "train.csv"
STATS_FILE = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "normalization"
    / "training_statistics.json"
)
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
    print("NORMALIZATION SANITY CHECK")
    print("=" * 70)

    with open(SPLIT_CSV, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)

    mean = np.array(stats["shared_mean"], dtype=np.float64)
    std = np.array(stats["shared_std"], dtype=np.float64)

    print(f"Training pairs available : {len(rows)}")
    print("Testing first 3 training pairs")
    print()

    for i, row in enumerate(rows[:3], start=1):
        lr_path = find_file(row["lr_file"])
        hr_path = find_file(row["hr_file"])

        with rasterio.open(lr_path) as src:
            lr = src.read().astype(np.float64)

        with rasterio.open(hr_path) as src:
            hr = src.read().astype(np.float64)

        lr_normalized = (lr - mean[:, None, None]) / std[:, None, None]
        hr_normalized = (hr - mean[:, None, None]) / std[:, None, None]

        print(f"Pair {i}:")
        print(f"  LR shape : {lr.shape}")
        print(f"  HR shape : {hr.shape}")

        print()
        print("  Normalized LR:")
        for c, name in enumerate(["B", "G", "R", "NIR"]):
            print(
                f"    {name}: "
                f"min={lr_normalized[c].min():.4f}, "
                f"max={lr_normalized[c].max():.4f}, "
                f"mean={lr_normalized[c].mean():.4f}, "
                f"std={lr_normalized[c].std():.4f}"
            )

        print()
        print("  Normalized HR:")
        for c, name in enumerate(["B", "G", "R", "NIR"]):
            print(
                f"    {name}: "
                f"min={hr_normalized[c].min():.4f}, "
                f"max={hr_normalized[c].max():.4f}, "
                f"mean={hr_normalized[c].mean():.4f}, "
                f"std={hr_normalized[c].std():.4f}"
            )

        print()
        print("-" * 70)

    print("=" * 70)
    print("NORMALIZATION SANITY CHECK: COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()