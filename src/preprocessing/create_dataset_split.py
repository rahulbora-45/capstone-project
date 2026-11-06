import csv
import random
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PAIR_CSV = PROJECT_ROOT / "results" / "audit" / "pair_validation.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "prepared" / "splits"

RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15


def main():
    print("=" * 70)
    print("DATASET SPLIT CREATION")
    print("=" * 70)

    # Read valid paired scenes
    rows = []

    with open(PAIR_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["status"] != "OK":
                continue

            lr_file = row["lr_file"]
            hr_file = row["hr_file"]

            # Spatial group is the numeric index after ANJI
            spatial_index = lr_file.split("_")[1]

            rows.append({
                "lr_file": lr_file,
                "hr_file": hr_file,
                "spatial_index": spatial_index,
            })

    print(f"Valid paired scenes : {len(rows)}")

    # Group scenes by spatial index
    groups = {}

    for row in rows:
        groups.setdefault(row["spatial_index"], []).append(row)

    spatial_groups = sorted(groups.keys(), key=int)

    print(f"Unique spatial groups: {len(spatial_groups)}")

    # Shuffle groups, not individual images
    rng = random.Random(RANDOM_SEED)
    rng.shuffle(spatial_groups)

    total_groups = len(spatial_groups)

    train_count = int(total_groups * TRAIN_RATIO)
    val_count = int(total_groups * VAL_RATIO)

    train_groups = spatial_groups[:train_count]
    val_groups = spatial_groups[train_count:train_count + val_count]
    test_groups = spatial_groups[train_count + val_count:]

    split_groups = {
        "train": set(train_groups),
        "val": set(val_groups),
        "test": set(test_groups),
    }

    print()
    print("Spatial group split:")
    print(f"  Train      : {len(train_groups)} groups")
    print(f"  Validation : {len(val_groups)} groups")
    print(f"  Test       : {len(test_groups)} groups")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Assign rows to splits
    split_rows = {
        "train": [],
        "val": [],
        "test": [],
    }

    for row in rows:
        spatial_index = row["spatial_index"]

        if spatial_index in split_groups["train"]:
            split = "train"
        elif spatial_index in split_groups["val"]:
            split = "val"
        else:
            split = "test"

        row["split"] = split
        split_rows[split].append(row)

    # Write manifests
    fieldnames = [
        "lr_file",
        "hr_file",
        "spatial_index",
        "split",
    ]

    for split, split_data in split_rows.items():
        output_file = OUTPUT_DIR / f"{split}.csv"

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(split_data)

    # Validate no spatial leakage
    train_indices = {
        row["spatial_index"] for row in split_rows["train"]
    }

    val_indices = {
        row["spatial_index"] for row in split_rows["val"]
    }

    test_indices = {
        row["spatial_index"] for row in split_rows["test"]
    }

    leakage = (
        train_indices & val_indices
        or train_indices & test_indices
        or val_indices & test_indices
    )

    print()
    print("Pair counts:")
    print(f"  Train      : {len(split_rows['train'])}")
    print(f"  Validation : {len(split_rows['val'])}")
    print(f"  Test       : {len(split_rows['test'])}")

    print()
    print(f"Spatial leakage: {bool(leakage)}")

    print()
    print("Output files:")
    print(f"  {OUTPUT_DIR / 'train.csv'}")
    print(f"  {OUTPUT_DIR / 'val.csv'}")
    print(f"  {OUTPUT_DIR / 'test.csv'}")

    if leakage:
        raise RuntimeError("Spatial leakage detected!")

    if len(split_rows["train"]) + \
       len(split_rows["val"]) + \
       len(split_rows["test"]) != len(rows):
        raise RuntimeError("Split pair counts do not match input!")

    print()
    print("=" * 70)
    print("DATASET SPLIT CREATION: PASS")
    print("=" * 70)


if __name__ == "__main__":
    main()