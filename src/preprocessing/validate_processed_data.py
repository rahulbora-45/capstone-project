from pathlib import Path

import pandas as pd
import rasterio


PAIR_CSV = Path("results/audit/pair_validation.csv")
EXTRACTED_ROOT = Path("data/extracted")
PROCESSED_ROOT = Path("data/processed/resampled_05m_to_10m")


def build_tiff_index():
    """Build an index of extracted TIFF files by filename."""

    index = {}

    for path in EXTRACTED_ROOT.rglob("*.tif"):
        if path.name in index:
            raise ValueError(f"Duplicate TIFF filename found: {path.name}")

        index[path.name] = path

    return index


def validate_output(processed_path, reference_path):
    """Validate one processed TIFF against its 10m reference."""

    with rasterio.open(processed_path) as processed, \
         rasterio.open(reference_path) as reference:

        checks = {
            "readable": True,
            "bands": processed.count == 4,
            "shape": (
                processed.height == reference.height
                and processed.width == reference.width
            ),
            "resolution": processed.res == reference.res,
            "crs": processed.crs == reference.crs,
            "bounds": processed.bounds == reference.bounds,
        }

        return checks, processed.dtypes


def main():

    print("=" * 70)
    print("PROCESSED DATA VALIDATION")
    print("=" * 70)

    if not PAIR_CSV.exists():
        raise FileNotFoundError(f"Pair CSV not found: {PAIR_CSV}")

    if not PROCESSED_ROOT.exists():
        raise FileNotFoundError(
            f"Processed directory not found: {PROCESSED_ROOT}"
        )

    pairs = pd.read_csv(PAIR_CSV)
    valid_pairs = pairs[pairs["status"] == "OK"]

    tiff_index = build_tiff_index()

    processed_files = list(PROCESSED_ROOT.glob("*.tif"))

    print(f"Validated input pairs : {len(valid_pairs)}")
    print(f"Processed TIFF files  : {len(processed_files)}")
    print()

    expected = len(valid_pairs)
    actual = len(processed_files)

    count_match = expected == actual

    print(f"File count match      : {count_match}")
    print()

    total = 0
    passed = 0
    failed = 0
    dtype_counts = {}
    failures = []

    for row in valid_pairs.itertuples(index=False):

        filename_10m = Path(row.lr_file).name
        filename_05m = Path(row.hr_file).name

        output_name = filename_05m.replace(
            ".tif",
            "_resampled_10m.tif"
        )

        processed_path = PROCESSED_ROOT / output_name

        total += 1

        if not processed_path.exists():
            failed += 1
            failures.append(
                f"Missing processed file: {output_name}"
            )
            continue

        if filename_10m not in tiff_index:
            failed += 1
            failures.append(
                f"Missing reference 10m file: {filename_10m}"
            )
            continue

        try:

            checks, dtypes = validate_output(
                processed_path,
                tiff_index[filename_10m],
            )

            dtype = dtypes[0]
            dtype_counts[dtype] = dtype_counts.get(dtype, 0) + 1

            if all(checks.values()):
                passed += 1
            else:
                failed += 1
                failed_checks = [
                    name
                    for name, result in checks.items()
                    if not result
                ]

                failures.append(
                    f"{output_name}: {', '.join(failed_checks)}"
                )

        except Exception as e:

            failed += 1
            failures.append(
                f"{output_name}: {e}"
            )

    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)

    print(f"Expected processed files : {expected}")
    print(f"Actual processed files   : {actual}")
    print(f"Count match              : {count_match}")
    print(f"Validation passed        : {passed}")
    print(f"Validation failed        : {failed}")

    print()
    print("Output data types:")

    for dtype, count in sorted(dtype_counts.items()):
        print(f"  {dtype}: {count}")

    print()

    if failures:
        print("FAILURES:")
        for failure in failures[:20]:
            print(f"  - {failure}")

        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")

    print("=" * 70)

    if count_match and failed == 0:
        print("STRUCTURAL VALIDATION: PASS")
    else:
        print("STRUCTURAL VALIDATION: FAIL")

    print("=" * 70)


if __name__ == "__main__":
    main()