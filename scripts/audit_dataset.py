
from pathlib import Path
import csv
import traceback

import numpy as np
import rasterio

DATA_ROOT = Path(r"D:\Dataset")
OUTPUT_DIR = Path(r"D:\Capstone")

band_report = OUTPUT_DIR / "audit_band_stats.csv"
file_report = OUTPUT_DIR / "audit_file_summary.csv"
error_report = OUTPUT_DIR / "audit_errors.csv"


def resolution_group(path):
    name = path.name.lower()
    if "_10m" in name:
        return "10m"
    if "_05m" in name:
        return "05m"
    if "_20m" in name:
        return "20m"
    return "unknown"


def main():
    files = sorted(
        p for p in DATA_ROOT.rglob("*")
        if p.is_file() and p.suffix.lower() in {".tif", ".tiff"}
    )

    print(f"Dataset root: {DATA_ROOT}")
    print(f"Extracted GeoTIFFs found: {len(files)}")

    band_fields = [
        "path", "group", "band", "width", "height", "dtype",
        "crs", "nodata", "resolution_x", "resolution_y",
        "minimum", "maximum", "mean",
        "negative_count", "zero_count", "valid_mask_count",
        "mask_invalid_count", "valid_negative_count",
        "valid_zero_count",
    ]

    file_fields = [
        "path", "group", "width", "height", "band_count",
        "dtype", "crs", "nodata", "resolution_x", "resolution_y",
        "expected_shape_for_group", "all_masks_valid", "status",
    ]

    error_fields = ["path", "error"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok_files = 0
    failed_files = 0
    negative_files = 0
    negative_band_rows = 0

    with (
        band_report.open("w", newline="", encoding="utf-8-sig") as bf,
        file_report.open("w", newline="", encoding="utf-8-sig") as ff,
        error_report.open("w", newline="", encoding="utf-8-sig") as ef
    ):
        bw = csv.DictWriter(bf, fieldnames=band_fields)
        fw = csv.DictWriter(ff, fieldnames=file_fields)
        ew = csv.DictWriter(ef, fieldnames=error_fields)

        bw.writeheader()
        fw.writeheader()
        ew.writeheader()

        for index, path in enumerate(files, start=1):
            try:
                with rasterio.open(path) as src:
                    group = resolution_group(path)
                    expected = {
                        "10m": (128, 128),
                        "05m": (256, 256),
                        "20m": (64, 64),
                    }.get(group)

                    masks_valid = True
                    file_has_negative = False

                    for band in range(1, src.count + 1):
                        arr = src.read(band)
                        mask = src.read_masks(band) > 0
                        valid = arr[mask]

                        if not mask.all():
                            masks_valid = False

                        neg_count = int(np.count_nonzero(arr < 0))
                        zero_count = int(np.count_nonzero(arr == 0))
                        valid_neg = int(np.count_nonzero(valid < 0))
                        valid_zero = int(np.count_nonzero(valid == 0))

                        if neg_count > 0:
                            file_has_negative = True
                            negative_band_rows += 1

                        bw.writerow({
                            "path": str(path),
                            "group": group,
                            "band": band,
                            "width": src.width,
                            "height": src.height,
                            "dtype": src.dtypes[band - 1],
                            "crs": str(src.crs),
                            "nodata": src.nodata,
                            "resolution_x": src.res[0],
                            "resolution_y": src.res[1],
                            "minimum": float(valid.min()) if valid.size else "",
                            "maximum": float(valid.max()) if valid.size else "",
                            "mean": float(valid.mean()) if valid.size else "",
                            "negative_count": neg_count,
                            "zero_count": zero_count,
                            "valid_mask_count": int(mask.sum()),
                            "mask_invalid_count": int((~mask).sum()),
                            "valid_negative_count": valid_neg,
                            "valid_zero_count": valid_zero,
                        })

                    shape = (src.height, src.width)
                    expected_ok = expected is None or shape == expected
                    status = "OK"

                    if src.crs is None:
                        status = "CHECK_MISSING_CRS"
                    elif not expected_ok:
                        status = "CHECK_UNEXPECTED_DIMENSIONS"
                    elif file_has_negative:
                        status = "CHECK_NEGATIVE_VALUES"
                    elif not masks_valid:
                        status = "CHECK_MASKED_PIXELS"

                    fw.writerow({
                        "path": str(path),
                        "group": group,
                        "width": src.width,
                        "height": src.height,
                        "band_count": src.count,
                        "dtype": ",".join(src.dtypes),
                        "crs": str(src.crs),
                        "nodata": src.nodata,
                        "resolution_x": src.res[0],
                        "resolution_y": src.res[1],
                        "expected_shape_for_group": (
                            str(expected) if expected else "not inferred"
                        ),
                        "all_masks_valid": masks_valid,
                        "status": status,
                    })

                    ok_files += 1
                    if file_has_negative:
                        negative_files += 1

            except Exception as exc:
                failed_files += 1
                ew.writerow({
                    "path": str(path),
                    "error": repr(exc),
                })

            if index % 100 == 0 or index == len(files):
                print(f"Processed {index}/{len(files)} files")

    print("\n=== AUDIT COMPLETE ===")
    print("Files discovered:", len(files))
    print("Files read successfully:", ok_files)
    print("Files with read errors:", failed_files)
    print("Files containing negative values:", negative_files)
    print("Band rows containing negative values:", negative_band_rows)
    print("\nReports saved:")
    print(band_report)
    print(file_report)
    print(error_report)


if __name__ == "__main__":
    main()
