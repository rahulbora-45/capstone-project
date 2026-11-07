import json
import math
from pathlib import Path

import rasterio
import torch

from src.models.super_resolution_cnn import SuperResolutionCNN


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "dataset"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "results"
    / "model_training"
    / "models"
    / "best_model.pth"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "results"
    / "model_evaluation"
)

RESULTS_FILE = (
    OUTPUT_ROOT
    / "test_evaluation.json"
)
NORMALIZATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "prepared"
    / "normalization"
    / "training_statistics.json"
)

TEST_LR_DIR = (
    DATASET_ROOT
    / "test"
    / "lr"
)

TEST_HR_DIR = (
    DATASET_ROOT
    / "test"
    / "hr"
)

DEVICE = torch.device("cpu")


# ============================================================
# SSIM
# ============================================================

def calculate_ssim(prediction, target):
    """
    Calculate global SSIM for one multispectral image.

    SSIM is calculated independently for each band and
    then averaged across the four bands.
    """

    prediction = prediction.astype("float64")
    target = target.astype("float64")

    band_ssim = []

    for band in range(prediction.shape[0]):

        pred = prediction[band]
        true = target[band]

        mean_pred = pred.mean()
        mean_true = true.mean()

        variance_pred = pred.var()
        variance_true = true.var()

        covariance = (
            (pred - mean_pred)
            * (true - mean_true)
        ).mean()

        data_range = (
            true.max() - true.min()
        )

        if data_range == 0:
            data_range = 1.0

        c1 = (
            0.01 * data_range
        ) ** 2

        c2 = (
            0.03 * data_range
        ) ** 2

        numerator = (
            (2 * mean_pred * mean_true + c1)
            * (2 * covariance + c2)
        )

        denominator = (
            (mean_pred ** 2 + mean_true ** 2 + c1)
            * (variance_pred + variance_true + c2)
        )

        ssim = numerator / denominator

        band_ssim.append(ssim)

    return band_ssim


# ============================================================
# Main evaluation
# ============================================================

def main():

    print("=" * 70)
    print("2× MULTISPECTRAL SUPER-RESOLUTION TEST EVALUATION")
    print("=" * 70)

    print(f"Device : {DEVICE}")

    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load checkpoint
    # --------------------------------------------------------

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
    )
    with open(
    NORMALIZATION_FILE,
    "r",
    encoding="utf-8",
    ) as file:
        normalization_stats = json.load(file)

    shared_mean = torch.tensor(
    normalization_stats["shared_mean"],
    dtype=torch.float32,
)

    shared_std = torch.tensor(
    normalization_stats["shared_std"],
    dtype=torch.float32,
)

    model = SuperResolutionCNN().to(DEVICE)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    print(
        f"Checkpoint epoch : {checkpoint['epoch']}"
    )

    print(
        f"Validation loss  : "
        f"{checkpoint['val_loss']:.6f}"
    )

    # --------------------------------------------------------
    # Test files
    # --------------------------------------------------------

    lr_files = sorted(
        TEST_LR_DIR.glob("*.tif")
    )

    if not lr_files:
        raise RuntimeError(
            f"No test LR files found in {TEST_LR_DIR}"
        )

    print(
        f"Test samples : {len(lr_files)}"
    )

    # --------------------------------------------------------
    # Accumulators
    # --------------------------------------------------------

    total_mae = 0.0
    total_rmse = 0.0
    total_psnr = 0.0
    total_ssim = 0.0

    band_mae = [0.0] * 4
    band_rmse = [0.0] * 4
    band_ssim = [0.0] * 4

    total_radiometric_mae = 0.0
    total_radiometric_rmse = 0.0
    total_radiometric_psnr = 0.0

    radiometric_band_mae = [0.0] * 4
    radiometric_band_rmse = [0.0] * 4

    total_samples = 0

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    with torch.no_grad():

        for index, lr_path in enumerate(
            lr_files,
            start=1,
        ):

            hr_path = (
                TEST_HR_DIR
                / lr_path.name.replace(
                    "_10m.tif",
                    "_05m.tif",
                )
            )

            if not hr_path.exists():
                raise RuntimeError(
                    f"Missing HR pair for: "
                    f"{lr_path.name}"
                )

            # ------------------------------------------------
            # Load data
            # ------------------------------------------------

            with rasterio.open(lr_path) as src:
                lr_array = (
                    src.read()
                    .astype("float32")
                )

            with rasterio.open(hr_path) as src:
                hr_array = (
                    src.read()
                    .astype("float32")
                )

            lr = (
                torch.from_numpy(lr_array)
                .unsqueeze(0)
                .to(DEVICE)
            )

            # ------------------------------------------------
            # Prediction
            # ------------------------------------------------

            prediction = model(lr)

            prediction_array = (
                prediction
                .squeeze(0)
                .cpu()
                .numpy()
            )
            # ------------------------------------------------
            # Denormalize prediction and HR target
            # ------------------------------------------------

            prediction_radiometric = (
                prediction_array
            * shared_std.numpy()[:, None, None]
            + shared_mean.numpy()[:, None, None]
                )

            hr_radiometric = (
             hr_array
            * shared_std.numpy()[:, None, None]
             + shared_mean.numpy()[:, None, None]
            )

            # ------------------------------------------------
            # Difference
            # ------------------------------------------------

            difference = (
                prediction_array
                - hr_array
            )

            absolute_error = (
                abs(difference)
            )

            squared_error = (
                difference ** 2
            )

            # ------------------------------------------------
            # Overall metrics
            # ------------------------------------------------

            mae = float(
                absolute_error.mean()
            )

            rmse = float(
                math.sqrt(
                    squared_error.mean()
                )
            )

            # ------------------------------------------------
            # PSNR
            #
            # Calculated in normalized space.
            # The target range is used as the data range.
            # ------------------------------------------------

            data_range = float(
                hr_array.max()
                - hr_array.min()
            )

            if data_range == 0:
                data_range = 1.0

            if rmse == 0:
                psnr = float("inf")
            else:
                psnr = (
                    20
                    * math.log10(
                        data_range / rmse
                    )
                )

            # ------------------------------------------------
            # SSIM
            # ------------------------------------------------

            image_ssim = calculate_ssim(
                prediction_array,
                hr_array,
            )

            mean_ssim = float(
                sum(image_ssim)
                / len(image_ssim)
            )

            # ------------------------------------------------
            # Per-band metrics
            # ------------------------------------------------

            image_band_mae = (
                absolute_error.mean(
                    axis=(1, 2)
                )
            )

            image_band_rmse = (
                squared_error.mean(
                    axis=(1, 2)
                ) ** 0.5
            )

            for band in range(4):

                band_mae[band] += float(
                    image_band_mae[band]
                )

                band_rmse[band] += float(
                    image_band_rmse[band]
                )

                band_ssim[band] += float(
                    image_ssim[band]
                )
            # ------------------------------------------------
            # Radiometric-space metrics
            # ------------------------------------------------

            radiometric_difference = (
                prediction_radiometric
                - hr_radiometric
            )

            radiometric_absolute_error = (
                abs(radiometric_difference)
            )

            radiometric_squared_error = (
                radiometric_difference ** 2
            )

            radiometric_mae = float(
                radiometric_absolute_error.mean()
            )

            radiometric_rmse = float(
                math.sqrt(
                    radiometric_squared_error.mean()
                )
            )

            radiometric_data_range = float(
                hr_radiometric.max()
                - hr_radiometric.min()
            )

            if radiometric_data_range == 0:
                radiometric_data_range = 1.0

            if radiometric_rmse == 0:
                radiometric_psnr = float("inf")
            else:
                radiometric_psnr = (
                    20
                    * math.log10(
                        radiometric_data_range
                        / radiometric_rmse
                    )
                )

            radiometric_band_mae_image = (
                radiometric_absolute_error.mean(
                    axis=(1, 2)
                )
            )

            radiometric_band_rmse_image = (
                radiometric_squared_error.mean(
                    axis=(1, 2)
                ) ** 0.5
            )

            for band in range(4):

                radiometric_band_mae[band] += float(
                    radiometric_band_mae_image[band]
                )

                radiometric_band_rmse[band] += float(
                    radiometric_band_rmse_image[band]
                )

            total_radiometric_mae += radiometric_mae
            total_radiometric_rmse += radiometric_rmse
            total_radiometric_psnr += radiometric_psnr

            # ------------------------------------------------
            # Accumulate
            # ------------------------------------------------

            total_mae += mae
            total_rmse += rmse
            total_psnr += psnr
            total_ssim += mean_ssim

            total_samples += 1

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if (
                index % 50 == 0
                or index == len(lr_files)
            ):

                print(
                    f"Processed "
                    f"{index}/{len(lr_files)} "
                    f"| MAE: {mae:.6f} "
                    f"| RMSE: {rmse:.6f} "
                    f"| PSNR: {psnr:.4f} "
                    f"| SSIM: {mean_ssim:.6f}"
                )

    # ========================================================
    # Final averages
    # ========================================================

    average_mae = (
        total_mae
        / total_samples
    )

    average_rmse = (
        total_rmse
        / total_samples
    )

    average_psnr = (
        total_psnr
        / total_samples
    )

    average_ssim = (
        total_ssim
        / total_samples
    )

    average_band_mae = [
        value / total_samples
        for value in band_mae
    ]

    average_band_rmse = [
        value / total_samples
        for value in band_rmse
    ]

    average_band_ssim = [
        value / total_samples
        for value in band_ssim
    ]
    average_radiometric_mae = (
    total_radiometric_mae
    / total_samples
)

    average_radiometric_rmse = (
        total_radiometric_rmse
        / total_samples
    )

    average_radiometric_psnr = (
        total_radiometric_psnr
        / total_samples
    )

    average_radiometric_band_mae = [
        value / total_samples
        for value in radiometric_band_mae
    ]

    average_radiometric_band_rmse = [
        value / total_samples
        for value in radiometric_band_rmse
    ]

    # ========================================================
    # Save results
    # ========================================================

    results = {

        "checkpoint_epoch": int(
            checkpoint["epoch"]
        ),

        "validation_l1": float(
            checkpoint["val_loss"]
        ),

        "test_samples": int(
            total_samples
        ),

        "metrics_space": "normalized",

        "mae": float(
            average_mae
        ),
        "radiometric_metrics_space": "original_radiometric",

        "radiometric_mae": float(
        average_radiometric_mae
        ),

        "radiometric_rmse": float(
        average_radiometric_rmse
        ),

        "radiometric_psnr": float(
        average_radiometric_psnr
        ),

        "rmse": float(
            average_rmse
        ),

        "psnr": float(
            average_psnr
        ),

        "ssim": float(
            average_ssim
        ),

        "per_band_mae": {

            "B": float(
                average_band_mae[0]
            ),

            "G": float(
                average_band_mae[1]
            ),

            "R": float(
                average_band_mae[2]
            ),

            "NIR": float(
                average_band_mae[3]
            ),
        },

        "per_band_rmse": {

            "B": float(
                average_band_rmse[0]
            ),

            "G": float(
                average_band_rmse[1]
            ),

            "R": float(
                average_band_rmse[2]
            ),

            "NIR": float(
                average_band_rmse[3]
            ),
        },

        "per_band_ssim": {

            "B": float(
                average_band_ssim[0]
            ),

            "G": float(
                average_band_ssim[1]
            ),

            "R": float(
                average_band_ssim[2]
            ),

            "NIR": float(
                average_band_ssim[3]
            ),
        },
        "radiometric_per_band_mae": {
    "B": float(
        average_radiometric_band_mae[0]
    ),
    "G": float(
        average_radiometric_band_mae[1]
    ),
    "R": float(
        average_radiometric_band_mae[2]
    ),
    "NIR": float(
        average_radiometric_band_mae[3]
    ),
},

"radiometric_per_band_rmse": {
    "B": float(
        average_radiometric_band_rmse[0]
    ),
    "G": float(
        average_radiometric_band_rmse[1]
    ),
    "R": float(
        average_radiometric_band_rmse[2]
    ),
    "NIR": float(
        average_radiometric_band_rmse[3]
    ),
},


    }

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            results,
            file,
            indent=4,
        )

    # ========================================================
    # Final output
    # ========================================================

    print()
    print("=" * 70)
    print("FULL TEST EVALUATION COMPLETE")
    print("=" * 70)

    print(
        f"Test samples       : "
        f"{total_samples}"
    )

    print(
        f"Average MAE        : "
        f"{average_mae:.6f}"
    )

    print(
        f"Average RMSE       : "
        f"{average_rmse:.6f}"
    )

    print(
        f"Average PSNR       : "
        f"{average_psnr:.4f}"
    )

    print(
        f"Average SSIM       : "
        f"{average_ssim:.6f}"
    )
    print()
    print("Original radiometric-space metrics:")

    print(
        f"  MAE  : "
        f"{average_radiometric_mae:.6f}"
    )

    print(
        f"  RMSE : "
        f"{average_radiometric_rmse:.6f}"
    )

    print(
        f"  PSNR : "
        f"{average_radiometric_psnr:.4f}"
    )

    print()
    print("Radiometric per-band MAE:")

    print(
        f"  B   : "
        f"{average_radiometric_band_mae[0]:.6f}"
    )

    print(
        f"  G   : "
        f"{average_radiometric_band_mae[1]:.6f}"
    )

    print(
        f"  R   : "
        f"{average_radiometric_band_mae[2]:.6f}"
    )

    print(
        f"  NIR : "
        f"{average_radiometric_band_mae[3]:.6f}"
    )

    print()
    print("Radiometric per-band RMSE:")

    print(
        f"  B   : "
        f"{average_radiometric_band_rmse[0]:.6f}"
    )

    print(
        f"  G   : "
        f"{average_radiometric_band_rmse[1]:.6f}"
    )

    print(
        f"  R   : "
        f"{average_radiometric_band_rmse[2]:.6f}"
    )

    print(
        f"  NIR : "
        f"{average_radiometric_band_rmse[3]:.6f}"
    )


    print()
    print("Per-band MAE:")

    print(
        f"  B   : "
        f"{average_band_mae[0]:.6f}"
    )

    print(
            f"  G   : "
            f"{average_band_mae[1]:.6f}"
        )

    print(
            f"  R   : "
            f"{average_band_mae[2]:.6f}"
        )

    print(
            f"  NIR : "
            f"{average_band_mae[3]:.6f}"
        )

    print()
    print("Per-band RMSE:")

    print(
            f"  B   : "
            f"{average_band_rmse[0]:.6f}"
        )

    print(
            f"  G   : "
            f"{average_band_rmse[1]:.6f}"
        )

    print(
            f"  R   : "
            f"{average_band_rmse[2]:.6f}"
        )

    print(
            f"  NIR : "
            f"{average_band_rmse[3]:.6f}"
        )

    print()
    print("Per-band SSIM:")

    print(
            f"  B   : "
            f"{average_band_ssim[0]:.6f}"
        )

    print(
            f"  G   : "
            f"{average_band_ssim[1]:.6f}"
        )

    print(
            f"  R   : "
            f"{average_band_ssim[2]:.6f}"
        )

    print(
            f"  NIR : "
            f"{average_band_ssim[3]:.6f}"
        )

    print()
    print(
            f"Results saved to   : "
            f"{RESULTS_FILE}"
        )


if __name__ == "__main__":
    main()
