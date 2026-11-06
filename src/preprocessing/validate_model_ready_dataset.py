import csv
import json
from pathlib import Path

import numpy as np
import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SPLITS_DIR = PROJECT_ROOT / "data" / "prepared" / "splits"
DATASET_DIR = PROJECT_ROOT / "data" / "prepared" / "dataset"
STATS_FILE = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "normalization"
    / "training_statistics.json"
)


def validate_split(split_name, mean, std):
    split_csv = SPLITS_DIR / f"{split_name}.csv"

    with open(split_csv, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    passed = 0
    failed = 0

    for i, row in enumerate(rows, start=1):
        lr_path = DATASET_DIR / split_name / "lr" / row["lr_file"]
        hr_path = DATASET_DIR / split_name / "hr" / row["hr_file"]

        try:
            if not lr_path.exists():
                raise FileNotFoundError(
                    f"Missing LR file: {lr_path.name}"
                )

            if not hr_path.exists():
                raise FileNotFoundError(
                    f"Missing HR file: {hr_path.name}"
                )

            with rasterio.open(lr_path) as src:
                lr = src.read()
                lr_shape = (src.count, src.height, src.width)
                lr_dtype = src.dtypes[0]
                lr_resolution = src.res
                lr_crs = src.crs
                lr_transform = src.transform

            with rasterio.open(hr_path) as src:
                hr = src.read()
                hr_shape = (src.count, src.height, src.width)
                hr_dtype = src.dtypes[0]
                hr_resolution = src.res
                hr_crs = src.crs
                hr_transform = src.transform

            if lr_shape != (4, 128, 128):
                raise ValueError(
                    f"Invalid LR shape: {lr_shape}"
                )

            if hr_shape != (4, 256, 256):
                raise ValueError(
                    f"Invalid HR shape: {hr_shape}"
                )

            if lr_dtype != "float32":
                raise ValueError(
                    f"Invalid LR dtype: {lr_dtype}"
                )

            if hr_dtype != "float32":
                raise ValueError(
                    f"Invalid HR dtype: {hr_dtype}"
                )

            if not np.allclose(
                lr_resolution,
                (10.0, 10.0),
                atol=1e-6
            ):
                raise ValueError(
                    f"Invalid LR resolution: {lr_resolution}"
                )

            if not np.allclose(
                hr_resolution,
                (5.0, 5.0),
                atol=1e-6
            ):
                raise ValueError(
                    f"Invalid HR resolution: {hr_resolution}"
                )

            if lr_crs != hr_crs:
                raise ValueError("LR/HR CRS mismatch")

            if not np.isfinite(lr).all():
                raise ValueError("LR contains NaN or infinite values")

            if not np.isfinite(hr).all():
                raise ValueError("HR contains NaN or infinite values")

            # Verify that the generated values are consistent with
            # the shared training normalization.
            lr_recovered = (
                lr * std[:, None, None]
                + mean[:, None, None]
            )

            hr_recovered = (
                hr * std[:, None, None]
                + mean[:, None, None]
            )

            if not np.isfinite(lr_recovered).all():
                raise ValueError("LR recovery produced invalid values")

            if not np.isfinite(hr_recovered).all():
                raise ValueError("HR recovery produced invalid values")

            passed += 1

        except Exception as e:
            failed += 1
            print()
            print(f"FAILED: {split_name} pair {i}")
            print(f"  LR: {row['lr_file']}")
            print(f"  HR: {row['hr_file']}")
            print(f"  Reason: {e}")

        if i % 250 == 0 or i == len(rows):
            print(
                f"Validated {i}/{len(rows)} {split_name} pairs..."
            )

    return len(rows), passed, failed


def main():
    print("=" * 70)
    print("MODEL-READY DATASET VALIDATION")
    print("=" * 70)

    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)

    mean = np.array(
        stats["shared_mean"],
        dtype=np.float32
    )

    std = np.array(
        stats["shared_std"],
        dtype=np.float32
    )

    print()
    print("Expected normalization:")
    print("  Method : per-band standardization")
    print("  Shared : LR and HR")
    print("  Clipping: None")

    total_expected = 0
    total_passed = 0
    total_failed = 0

    split_results = {}

    for split_name in ["train", "val", "test"]:
        print()
        print("-" * 70)
        print(f"VALIDATING {split_name.upper()}")

        expected, passed, failed = validate_split(
            split_name,
            mean,
            std
        )

        split_results[split_name] = {
            "expected": expected,
            "passed": passed,
            "failed": failed
        }

        total_expected += expected
        total_passed += passed
        total_failed += failed

        print(f"{split_name} expected : {expected}")
        print(f"{split_name} passed   : {passed}")
        print(f"{split_name} failed   : {failed}")

    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    print(f"Expected total pairs : {total_expected}")
    print(f"Validation passed    : {total_passed}")
    print(f"Validation failed    : {total_failed}")

    print()
    print("Split summary:")

    for split_name in ["train", "val", "test"]:
        result = split_results[split_name]

        print(
            f"  {split_name:<5} : "
            f"{result['passed']}/{result['expected']} passed"
        )

    print()

    if (
        total_failed == 0
        and total_passed == total_expected
        and total_expected == 2312
    ):
        print("MODEL-READY DATASET VALIDATION: PASS")
    else:
        print("MODEL-READY DATASET VALIDATION: FAIL")


if __name__ == "__main__":
    main()