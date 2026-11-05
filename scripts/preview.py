
import rasterio
import numpy as np
import matplotlib.pyplot as plt

input_path = r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_10m\b2b3b4b8\10m\ANJI_0_2020-04-08_50RQV_b2b3b4b8_10m.tif"

reference_path = r"D:\Dataset\ANJI\ANJI\ANJI_2020-04-08_50RQV_b2b3b4b8_05m\b2b3b4b8\05m\ANJI_1_2020-04-08_50RQV_b2b3b4b8_05m.tif"


def make_rgb(path):
    with rasterio.open(path) as src:
        # Bands: B2=1, B3=2, B4=3, B8=4
        rgb = src.read([3, 2, 1]).astype(np.float32)

        # Scale each band independently for display
        for i in range(3):
            band = rgb[i]
            valid = np.isfinite(band)

            if src.nodata is not None:
                valid &= band != src.nodata

            if valid.any():
                low, high = np.percentile(
                    band[valid], [2, 98]
                )
                rgb[i] = np.clip(
                    (band - low) / max(high - low, 1e-6),
                    0, 1
                )

        return np.moveaxis(rgb, 0, -1)


input_rgb = make_rgb(input_path)
reference_rgb = make_rgb(reference_path)

fig, axes = plt.subplots(1, 2, figsize=(10, 5))

axes[0].imshow(input_rgb)
axes[0].set_title("10m Sentinel-2 Input")
axes[0].axis("off")

axes[1].imshow(reference_rgb)
axes[1].set_title("5m Reference")
axes[1].axis("off")

plt.tight_layout()
plt.savefig("satellite_preview.png", dpi=150)
plt.show()
