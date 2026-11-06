from pathlib import Path

import rasterio


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REFERENCE_10M = (
    PROJECT_ROOT
    / "data"
    / "extracted"
    / "ANJI"
    / "ANJI"
    / "ANJI_2020-04-08_50RQV_b2b3b4b8_10m"
    / "b2b3b4b8"
    / "10m"
    / "ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
)

RESAMPLED_05M = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "resampled_05m_to_10m"
    / "ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m_resampled_10m.tif"
)

OUTPUT_8CHANNEL = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "8channel"
    / "ANJI_0_2020-04-08_50RQV_b2b3b4b8_8channel.tif"
)


# ============================================================
# VALIDATION
# ============================================================

print("=" * 70)
print("8-CHANNEL PILOT VALIDATION")
print("=" * 70)

with rasterio.open(REFERENCE_10M) as ref, \
     rasterio.open(RESAMPLED_05M) as resampled, \
     rasterio.open(OUTPUT_8CHANNEL) as output:

    checks = {}

    # --------------------------------------------------------
    # Band count
    # --------------------------------------------------------

    checks["band_count"] = output.count == 8

    # --------------------------------------------------------
    # Dtype
    # --------------------------------------------------------

    checks["dtype"] = all(
        dtype == "float32"
        for dtype in output.dtypes
    )

    # --------------------------------------------------------
    # Shape
    # --------------------------------------------------------

    checks["shape"] = (
        output.width == ref.width
        and output.height == ref.height
    )

    # --------------------------------------------------------
    # Resolution
    # --------------------------------------------------------

    checks["resolution"] = (
        output.res == ref.res
    )

    # --------------------------------------------------------
    # CRS
    # --------------------------------------------------------

    checks["crs"] = (
        output.crs == ref.crs
    )

    # --------------------------------------------------------
    # Transform / grid
    # --------------------------------------------------------

    checks["transform"] = (
        output.transform == ref.transform
    )

    # --------------------------------------------------------
    # Bounds
    # --------------------------------------------------------

    checks["bounds"] = (
        output.bounds == ref.bounds
    )

    # --------------------------------------------------------
    # Dimensions of the two source datasets
    # --------------------------------------------------------

    checks["source_10m_shape"] = (
        output.width == ref.width
        and output.height == ref.height
    )

    checks["source_resampled_shape"] = (
        output.width == resampled.width
        and output.height == resampled.height
    )

    # --------------------------------------------------------
    # Channel grouping
    # --------------------------------------------------------

    # Read one pixel from each source and corresponding
    # channels from the 8-channel output.
    ref_pixel = ref.read(window=((0, 1), (0, 1)))
    resampled_pixel = resampled.read(window=((0, 1), (0, 1)))
    output_pixel = output.read(window=((0, 1), (0, 1)))

    checks["channels_1_to_4_match_10m"] = (
        (output_pixel[:4] == ref_pixel).all()
    )

    checks["channels_5_to_8_match_resampled"] = (
        (output_pixel[4:] == resampled_pixel).all()
    )

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print()
    print("Validation checks:")
    print()

    for name, result in checks.items():
        print(f"{name:40} : {result}")

    print()
    print("=" * 70)

    if all(checks.values()):
        print("8-CHANNEL PILOT VALIDATION: PASS")
    else:
        print("8-CHANNEL PILOT VALIDATION: FAIL")

    print("=" * 70)