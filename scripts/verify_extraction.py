import os
import glob
import rasterio

ROOT = "data/extracted"

total = 0
failed = 0
failed_files = []

for dataset in sorted(os.listdir(ROOT)):
    dataset_path = os.path.join(ROOT, dataset)

    if not os.path.isdir(dataset_path):
        continue

    print(f"\n===== {dataset} =====")

    dataset_total = 0
    dataset_failed = 0

    tif_files = glob.glob(
        os.path.join(dataset_path, "**", "*.tif"),
        recursive=True
    )

    for tif_file in tif_files:
        total += 1
        dataset_total += 1

        try:
            with rasterio.open(tif_file) as src:
                _ = src.width
                _ = src.height
                _ = src.count
                _ = src.crs
                _ = src.transform

        except Exception as e:
            failed += 1
            dataset_failed += 1
            failed_files.append((tif_file, str(e)))

    print(f"TIFF files: {dataset_total}")
    print(f"Failed: {dataset_failed}")

print("\n===== FINAL RESULT =====")
print(f"Total TIFF files checked: {total}")
print(f"Failed TIFF files: {failed}")

if failed_files:
    print("\nFirst 20 failures:")
    for path, error in failed_files[:20]:
        print(f"\n{path}")
        print(f"Error: {error}")

    raise SystemExit(1)

print("ALL TIFF FILES ARE READABLE.")