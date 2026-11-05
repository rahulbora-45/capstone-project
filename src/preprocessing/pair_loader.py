from pathlib import Path
import rasterio


def inspect_pair(input_10m: str, input_05m: str) -> dict:
    """
    Inspect one 10m/5m satellite image pair.

    The source TIFF files are opened in read-only mode and are
    never modified.
    """

    input_10m = Path(input_10m)
    input_05m = Path(input_05m)

    if not input_10m.exists():
        raise FileNotFoundError(f"10m file not found: {input_10m}")

    if not input_05m.exists():
        raise FileNotFoundError(f"05m file not found: {input_05m}")

    with rasterio.open(input_10m) as src_10m, rasterio.open(input_05m) as src_05m:

        if src_10m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 10m image, found {src_10m.count}"
            )

        if src_05m.count != 4:
            raise ValueError(
                f"Expected 4 bands in 05m image, found {src_05m.count}"
            )

        if src_10m.crs != src_05m.crs:
            raise ValueError("CRS mismatch between 10m and 05m images")

        if src_10m.bounds != src_05m.bounds:
            raise ValueError("Spatial bounds mismatch between 10m and 05m images")

        if src_10m.width * 2 != src_05m.width:
            raise ValueError("05m width is not 2x the 10m width")

        if src_10m.height * 2 != src_05m.height:
            raise ValueError("05m height is not 2x the 10m height")

        return {
            "10m_path": str(input_10m),
            "05m_path": str(input_05m),
            "10m_shape": (src_10m.height, src_10m.width),
            "05m_shape": (src_05m.height, src_05m.width),
            "10m_bands": src_10m.count,
            "05m_bands": src_05m.count,
            "10m_resolution": src_10m.res,
            "05m_resolution": src_05m.res,
            "crs": str(src_10m.crs),
            "bounds": tuple(src_10m.bounds),
        }


if __name__ == "__main__":

    pair = inspect_pair(
        r"data\extracted\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif",
        r"data\extracted\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_05m\b2b3b4b8\05m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_05m.tif",
    )

    print("=" * 70)
    print("PREPROCESSING PAIR INSPECTION")
    print("=" * 70)

    for key, value in pair.items():
        print(f"{key}: {value}")