import os
import csv
import rasterio


PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

PAIR_CSV = os.path.join(
    PROJECT_ROOT,
    "results",
    "audit",
    "pair_validation.csv"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "8channel"
)

EXTRACTED_DIR = os.path.join(
    PROJECT_ROOT,
    "data",
    "extracted"
)


def build_file_index(root_dir):
    index = {}

    for root, _, files in os.walk(root_dir):
        for filename in files:
            if filename.lower().endswith(".tif"):
                index[filename] = os.path.join(root, filename)

    return index


def main():

    print("=" * 70)
    print("8-CHANNEL DATASET VALIDATION")
    print("=" * 70)

    extracted_index = build_file_index(EXTRACTED_DIR)
    output_index = build_file_index(OUTPUT_DIR)

    expected_outputs = []

    with open(PAIR_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:

            if row.get("status", "").strip().upper() != "OK":
                continue

            filename_10m = os.path.basename(
                row["lr_file"].strip()
            )

            if not filename_10m.endswith("_10m.tif"):
                continue

            output_filename = filename_10m.replace(
                "_10m.tif",
                "_8channel.tif"
            )

            expected_outputs.append(
                (filename_10m, output_filename)
            )

    expected_count = len(expected_outputs)
    actual_count = len(output_index)

    print()
    print(f"Expected 8-channel files : {expected_count}")
    print(f"Actual 8-channel files   : {actual_count}")
    print(f"Count match              : {expected_count == actual_count}")
    print()

    passed = 0
    failed = 0

    dtype_counts = {}

    for index, (reference_filename, output_filename) in enumerate(
        expected_outputs,
        start=1
    ):

        output_path = output_index.get(output_filename)
        reference_path = extracted_index.get(reference_filename)

        file_passed = True

        if output_path is None:
            print(
                f"[{index}/{expected_count}] "
                f"MISSING: {output_filename}"
            )
            failed += 1
            continue

        if reference_path is None:
            print(
                f"[{index}/{expected_count}] "
                f"REFERENCE MISSING: {reference_filename}"
            )
            failed += 1
            continue

        try:

            with rasterio.open(output_path) as output_ds, \
                 rasterio.open(reference_path) as reference_ds:

                if output_ds.count != 8:
                    file_passed = False

                if any(
                    dtype != "float32"
                    for dtype in output_ds.dtypes
                ):
                    file_passed = False

                if (
                    output_ds.width != reference_ds.width
                    or output_ds.height != reference_ds.height
                ):
                    file_passed = False

                if output_ds.res != reference_ds.res:
                    file_passed = False

                if output_ds.crs != reference_ds.crs:
                    file_passed = False

                if output_ds.transform != reference_ds.transform:
                    file_passed = False

                if output_ds.bounds != reference_ds.bounds:
                    file_passed = False

                for dtype in output_ds.dtypes:
                    dtype_counts[dtype] = (
                        dtype_counts.get(dtype, 0) + 1
                    )

        except Exception as e:

            file_passed = False

            print(
                f"[{index}/{expected_count}] "
                f"ERROR: {output_filename} -> {e}"
            )

        if file_passed:
            passed += 1
        else:
            failed += 1
            print(
                f"[{index}/{expected_count}] "
                f"FAILED: {output_filename}"
            )

        if index % 250 == 0:
            print(
                f"Processed {index}/{expected_count} files..."
            )

    print()
    print("=" * 70)
    print("8-CHANNEL DATASET VALIDATION COMPLETE")
    print("=" * 70)

    print(f"Expected 8-channel files : {expected_count}")
    print(f"Actual 8-channel files   : {actual_count}")
    print(f"Count match              : {expected_count == actual_count}")
    print(f"Validation passed        : {passed}")
    print(f"Validation failed        : {failed}")

    print()
    print("Output data types:")

    for dtype, count in sorted(dtype_counts.items()):
        print(f"  {dtype}: {count}")

    print()

    if (
        expected_count == actual_count
        and passed == expected_count
        and failed == 0
        and set(dtype_counts.keys()) == {"float32"}
    ):
        print("8-CHANNEL DATASET VALIDATION: PASS")
    else:
        print("8-CHANNEL DATASET VALIDATION: FAIL")


if __name__ == "__main__":
    main()