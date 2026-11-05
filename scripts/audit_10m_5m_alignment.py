import os
import glob
import csv
import rasterio

ROOT = r"D:\Capstone-Project\data\extracted"

DATASETS = [
    "ANJI",
    "ARM",
    "BAMBENW2",
    "ES-IC3XG"
]

EXPECTED_10M_SHAPE = (128, 128)
EXPECTED_5M_SHAPE = (256, 256)

TOLERANCE = 1e-6


def find_files(dataset, resolution):
    root = os.path.join(ROOT, dataset)

    return sorted(
        glob.glob(
            os.path.join(root, "**", f"*_{resolution}.tif"),
            recursive=True
        )
    )


def make_pair_key(filename):
    name = os.path.basename(filename)

    if name.endswith("_10m.tif"):
        return name[:-8]

    if name.endswith("_05m.tif"):
        return name[:-8]

    return None


def check_resolution_relationship(res10, res5):
    return (
        abs(res10[0] / 2 - res5[0]) <= TOLERANCE
        and
        abs(res10[1] / 2 - res5[1]) <= TOLERANCE
    )


def check_bounds(bounds10, bounds5):
    return (
        abs(bounds10.left - bounds5.left) <= TOLERANCE
        and
        abs(bounds10.right - bounds5.right) <= TOLERANCE
        and
        abs(bounds10.top - bounds5.top) <= TOLERANCE
        and
        abs(bounds10.bottom - bounds5.bottom) <= TOLERANCE
    )


def check_transform_alignment(transform10, transform5):
    # 5m grid should have half the pixel size
    # and the same upper-left origin.
    return (
        abs(transform10.c - transform5.c) <= TOLERANCE
        and
        abs(transform10.f - transform5.f) <= TOLERANCE
        and
        abs(transform10.a / 2 - transform5.a) <= TOLERANCE
        and
        abs(transform10.e / 2 - transform5.e) <= TOLERANCE
    )


print("=" * 75)
print("10m ↔ 5m PAIRING AND SPATIAL ALIGNMENT AUDIT")
print("=" * 75)

overall_results = []

for dataset in DATASETS:

    print()
    print("=" * 75)
    print(f"DATASET: {dataset}")
    print("=" * 75)

    files10 = find_files(dataset, "10m")
    files5 = find_files(dataset, "05m")

    print(f"10m files found: {len(files10)}")
    print(f"5m files found:  {len(files5)}")

    map10 = {
        make_pair_key(f): f
        for f in files10
    }

    map5 = {
        make_pair_key(f): f
        for f in files5
    }

    keys10 = set(map10.keys())
    keys5 = set(map5.keys())

    missing_5m = keys10 - keys5
    missing_10m = keys5 - keys10

    print(f"Missing 5m pairs:  {len(missing_5m)}")
    print(f"Missing 10m pairs: {len(missing_10m)}")

    paired_keys = sorted(keys10 & keys5)

    pairing_pass = (
        len(missing_5m) == 0
        and len(missing_10m) == 0
    )

    print(f"Filename pairing:  {'PASS' if pairing_pass else 'FAIL'}")

    alignment_failures = []

    for i, key in enumerate(paired_keys, start=1):

        path10 = map10[key]
        path5 = map5[key]

        try:
            with rasterio.open(path10) as src10, \
                 rasterio.open(path5) as src5:

                shape10 = (src10.height, src10.width)
                shape5 = (src5.height, src5.width)

                shape_ok = (
                    shape10 == EXPECTED_10M_SHAPE
                    and
                    shape5 == EXPECTED_5M_SHAPE
                )

                crs_ok = (
                    src10.crs is not None
                    and
                    src5.crs is not None
                    and
                    src10.crs == src5.crs
                )

                resolution_ok = check_resolution_relationship(
                    src10.res,
                    src5.res
                )

                bounds_ok = check_bounds(
                    src10.bounds,
                    src5.bounds
                )

                transform_ok = check_transform_alignment(
                    src10.transform,
                    src5.transform
                )

                pair_ok = (
                    shape_ok
                    and crs_ok
                    and resolution_ok
                    and bounds_ok
                    and transform_ok
                )

                if not pair_ok:

                    alignment_failures.append({
                        "key": key,
                        "shape10": shape10,
                        "shape5": shape5,
                        "crs10": str(src10.crs),
                        "crs5": str(src5.crs),
                        "res10": src10.res,
                        "res5": src5.res,
                        "bounds10": src10.bounds,
                        "bounds5": src5.bounds,
                        "shape_ok": shape_ok,
                        "crs_ok": crs_ok,
                        "resolution_ok": resolution_ok,
                        "bounds_ok": bounds_ok,
                        "transform_ok": transform_ok
                    })

        except Exception as e:

            alignment_failures.append({
                "key": key,
                "error": str(e)
            })

        if i % 500 == 0:
            print(f"Checked {i}/{len(paired_keys)} pairs...")

    alignment_pass = len(alignment_failures) == 0

    print()
    print(f"Pairs checked:             {len(paired_keys)}")
    print(
        f"Spatial alignment:         "
        f"{'PASS' if alignment_pass else 'FAIL'}"
    )
    print(f"Alignment failures:        {len(alignment_failures)}")

    dataset_pass = pairing_pass and alignment_pass

    print()
    print(
        f"FINAL DATASET STATUS:      "
        f"{'PASS' if dataset_pass else 'REVIEW'}"
    )

    overall_results.append({
        "dataset": dataset,
        "10m_files": len(files10),
        "5m_files": len(files5),
        "pairs_checked": len(paired_keys),
        "missing_5m": len(missing_5m),
        "missing_10m": len(missing_10m),
        "alignment_failures": len(alignment_failures),
        "pairing_status": "PASS" if pairing_pass else "FAIL",
        "alignment_status": "PASS" if alignment_pass else "FAIL",
        "final_status": "PASS" if dataset_pass else "REVIEW"
    })

    if alignment_failures:
        print()
        print("First alignment failure:")
        print(alignment_failures[0])


os.makedirs(
    os.path.join(ROOT, "..", "..", "results", "audit"),
    exist_ok=True
)

output_path = os.path.join(
    ROOT,
    "..",
    "..",
    "results",
    "audit",
    "alignment_audit_summary.csv"
)

with open(output_path, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=overall_results[0].keys()
    )

    writer.writeheader()
    writer.writerows(overall_results)


print()
print("=" * 75)
print("OVERALL SUMMARY")
print("=" * 75)

for result in overall_results:

    print(
        f"{result['dataset']}: "
        f"{result['final_status']} | "
        f"Pairs={result['pairs_checked']} | "
        f"Alignment failures={result['alignment_failures']}"
    )

print()
print(f"Summary saved to: {output_path}")

print("=" * 75)
print("AUDIT COMPLETE")
print("=" * 75)