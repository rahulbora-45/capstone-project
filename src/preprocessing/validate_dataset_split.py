import csv
from pathlib import Path

import rasterio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PAIR_CSV = PROJECT_ROOT / "results" / "audit" / "pair_validation.csv"
SPLIT_DIR = PROJECT_ROOT / "data" / "prepared" / "splits"
EXTRACTED_DIR = PROJECT_ROOT / "data" / "extracted" / "ANJI"


EXPECTED_SPLITS = ["train", "val", "test"]


def find_file(filename):
    matches = list(EXTRACTED_DIR.rglob(filename))

    if len(matches) != 1:
        return None

    return matches[0]


def validate_raster(path, expected_height, expected_width, expected_resolution):
    errors = []

    try:
        with rasterio.open(path) as src:
            if src.count != 4:
                errors.append(f"bands={src.count}")

            if src.height != expected_height or src.width != expected_width:
                errors.append(
                    f"shape={src.height}x{src.width}"
                )

            if src.res != expected_resolution:
                errors.append(
                    f"resolution={src.res}"
                )

    except Exception as e:
        errors.append(f"open_error={e}")

    return errors


def main():
    print("=" * 70)
    print("DATASET SPLIT VALIDATION")
    print("=" * 70)

    all_rows = []
    split_rows = {}

    for split in EXPECTED_SPLITS:
        csv_path = SPLIT_DIR / f"{split}.csv"

        if not csv_path.exists():
            raise FileNotFoundError(f"Missing split file: {csv_path}")

        rows = []

        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                rows.append(row)
                all_rows.append(row)

        split_rows[split] = rows

        print(f"{split:>5} pairs : {len(rows)}")

    print()
    print("Validating raster files...")

    passed = 0
    failed = 0
    seen_pairs = set()
    errors = []

    for split, rows in split_rows.items():

        for i, row in enumerate(rows, start=1):

            lr_file = row["lr_file"]
            hr_file = row["hr_file"]
            spatial_index = row["spatial_index"]

            pair_key = (lr_file, hr_file)

            if pair_key in seen_pairs:
                errors.append(
                    f"Duplicate pair across splits: {lr_file}"
                )
                failed += 1
                continue

            seen_pairs.add(pair_key)

            lr_path = find_file(lr_file)
            hr_path = find_file(hr_file)

            row_errors = []

            if lr_path is None:
                row_errors.append("LR file missing or ambiguous")

            if hr_path is None:
                row_errors.append("HR file missing or ambiguous")

            if lr_path is not None:
                row_errors.extend(
                    [
                        f"LR {e}"
                        for e in validate_raster(
                            lr_path,
                            128,
                            128,
                            (10.0, 10.0),
                        )
                    ]
                )

            if hr_path is not None:
                row_errors.extend(
                    [
                        f"HR {e}"
                        for e in validate_raster(
                            hr_path,
                            256,
                            256,
                            (5.0, 5.0),
                        )
                    ]
                )

            if row_errors:
                failed += 1

                if len(errors) < 20:
                    errors.append(
                        f"{split} row {i} "
                        f"(spatial_index={spatial_index}): "
                        + "; ".join(row_errors)
                    )
            else:
                passed += 1

    # Check spatial-index leakage
    split_indices = {}

    for split, rows in split_rows.items():
        split_indices[split] = {
            row["spatial_index"]
            for row in rows
        }

    train_val = split_indices["train"] & split_indices["val"]
    train_test = split_indices["train"] & split_indices["test"]
    val_test = split_indices["val"] & split_indices["test"]

    leakage = train_val or train_test or val_test

    print()
    print("=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    print(f"Expected total pairs : {len(all_rows)}")
    print(f"Unique pairs         : {len(seen_pairs)}")
    print(f"Validation passed    : {passed}")
    print(f"Validation failed    : {failed}")

    print()
    print("Spatial-index leakage:")
    print(f"  Train/Val  : {len(train_val)}")
    print(f"  Train/Test : {len(train_test)}")
    print(f"  Val/Test   : {len(val_test)}")

    if errors:
        print()
        print("First validation errors:")

        for error in errors:
            print(f"  - {error}")

    total_expected = 1583 + 351 + 378

    if (
        len(all_rows) != total_expected
        or len(seen_pairs) != total_expected
        or failed != 0
        or leakage
    ):
        print()
        print("DATASET SPLIT VALIDATION: FAIL")
        raise SystemExit(1)

    print()
    print("DATASET SPLIT VALIDATION: PASS")


if __name__ == "__main__":
    main()