from pathlib import Path

import rasterio
from rasterio.enums import Resampling


def resample_05m_to_10m(input_05m: str, reference_10m: str, output_path: str):
    """
    Resample a 5m four-band image onto the grid of a 10m reference image.

    The original input files are opened in read-only mode and are never modified.
    """

    input_05m = Path(input_05m)
    reference_10m = Path(reference_10m)
    output_path = Path(output_path)

    if not input_05m.exists():
        raise FileNotFoundError(f"05m file not found: {input_05m}")

    if not reference_10m.exists():
        raise FileNotFoundError(f"10m reference file not found: {reference_10m}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(input_05m) as src_05m, rasterio.open(reference_10m) as src_10m:

        if src_05m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 05m image, found {src_05m.count}"
            )

        if src_10m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 10m reference, found {src_10m.count}"
            )

        if src_05m.crs != src_10m.crs:
            raise ValueError("CRS mismatch between 05m and 10m images")

        profile = src_05m.profile.copy()

        profile.update(
            driver="GTiff",
            height=src_10m.height,
            width=src_10m.width,
            transform=src_10m.transform,
            crs=src_10m.crs,
            dtype=src_05m.dtypes[0],
            count=src_05m.count,
        )

        with rasterio.open(output_path, "w", **profile) as dst:

            for band in range(1, src_05m.count + 1):
                data = src_05m.read(
                    band,
                    out_shape=(src_10m.height, src_10m.width),
                    resampling=Resampling.bilinear,
                )

                dst.write(data, band)

        return {
            "output_path": str(output_path),
            "shape": (src_10m.height, src_10m.width),
            "bands": src_05m.count,
            "resolution": src_10m.res,
            "crs": str(src_10m.crs),
        }


if __name__ == "__main__":

    input_05m = (
        r"data\extracted\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_05m\b2b3b4b8\05m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif"
    )

    reference_10m = (
        r"data\extracted\ANJI\ANJI"
        r"\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"
    )

    output_path = (
        r"data\processed\ANJI"
        r"\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m_resampled_10m.tif"
    )

    result = resample_05m_to_10m(
        input_05m,
        reference_10m,
        output_path,
    )

    print("=" * 70)
    print("5m → 10m PREPROCESSING PILOT")
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")

    print("=" * 70)
    print("PREPROCESSING PILOT COMPLETE")
    print("=" * 70)