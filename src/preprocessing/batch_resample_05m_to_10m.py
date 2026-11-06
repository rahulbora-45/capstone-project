from pathlib import Path

import pandas as pd
import rasterio
from rasterio.enums import Resampling


PAIR_CSV = Path("results/audit/pair_validation.csv")
EXTRACTED_ROOT = Path("data/extracted")
OUTPUT_ROOT = Path("data/processed/resampled_05m_to_10m")


def build_tiff_index():
    """Build a filename → actual TIFF path index."""

    print("Building TIFF file index...")

    index = {}

    for path in EXTRACTED_ROOT.rglob("*.tif"):
        filename = path.name

        if filename in index:
            raise ValueError(
                f"Duplicate TIFF filename found:\n"
                f"  {index[filename]}\n"
                f"  {path}"
            )

        index[filename] = path

    print(f"Indexed TIFF files: {len(index)}")

    return index


def resample_pair(input_05m: Path, reference_10m: Path, output_path: Path):
    """Resample one 5m image onto the corresponding 10m grid."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_05m) as src_05m, rasterio.open(reference_10m) as src_10m:

        if src_05m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 05m image, found {src_05m.count}"
            )

        if src_10m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 10m image, found {src_10m.count}"
            )

        if src_05m.crs != src_10m.crs:
            raise ValueError("CRS mismatch")

        profile = src_05m.profile.copy()

        profile.update(
            driver="GTiff",
            height=src_10m.height,
            width=src_10m.width,
            transform=src_10m.transform,
            crs=src_10m.crs,
            count=src_05m.count,
            dtype="float32",
        )

        with rasterio.open(output_path, "w", **profile) as dst:

            for band in range(1, src_05m.count + 1):

                data = src_05m.read(
                    band,
                    out_shape=(src_10m.height, src_10m.width),
                    resampling=Resampling.bilinear,
                )

                dst.write(data, band)


def main():

    if not PAIR_CSV.exists():
        raise FileNotFoundError(
            f"Pair validation file not found: {PAIR_CSV}"
        )

    if not EXTRACTED_ROOT.exists():
        raise FileNotFoundError(
            f"Extracted data directory not found: {EXTRACTED_ROOT}"
        )

    pairs = pd.read_csv(PAIR_CSV)

    valid_pairs = pairs[pairs["status"] == "OK"]

    print("=" * 70)
    print("BATCH 5m → 10m PREPROCESSING")
    print("=" * 70)
    print(f"Validated pairs: {len(valid_pairs)}")
    print()

    # Find the real locations of all extracted TIFF files.
    tiff_index = build_tiff_index()

    print()

    success = 0
    skipped = 0
    failed = 0

    for i, row in enumerate(valid_pairs.itertuples(index=False), start=1):

        filename_10m = Path(row.lr_file).name
        filename_05m = Path(row.hr_file).name

        print(f"[{i}/{len(valid_pairs)}] {filename_05m}")

        if filename_10m not in tiff_index:
            failed += 1
            print(f"  → FAILED: 10m file not found: {filename_10m}")
            continue

        if filename_05m not in tiff_index:
            failed += 1
            print(f"  → FAILED: 05m file not found: {filename_05m}")
            continue

        input_10m = tiff_index[filename_10m]
        input_05m = tiff_index[filename_05m]

        output_name = filename_05m.replace(
            ".tif",
            "_resampled_10m.tif"
        )

        output_path = OUTPUT_ROOT / output_name

        if output_path.exists():
            output_path.unlink()
            print("  → Existing output removed; regenerating as float32")
            

        try:

            resample_pair(
                input_05m=input_05m,
                reference_10m=input_10m,
                output_path=output_path,
            )

            success += 1
            print("  → SUCCESS")

        except Exception as e:

            failed += 1
            print(f"  → FAILED: {e}")

    print()
    print("=" * 70)
    print("BATCH PREPROCESSING COMPLETE")
    print("=" * 70)
    print(f"Successful : {success}")
    print(f"Skipped    : {skipped}")
    print(f"Failed     : {failed}")
    print(f"Total      : {len(valid_pairs)}")
    print("=" * 70)


if __name__ == "__main__":
    main()