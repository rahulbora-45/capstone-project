import json
from pathlib import Path

import rasterio
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from src.models.super_resolution_cnn import SuperResolutionCNN


# ============================================================
# Configuration
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_ROOT = PROJECT_ROOT / "data" / "prepared" / "dataset"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "model_training"

MODEL_DIR = OUTPUT_ROOT / "models"
HISTORY_FILE = OUTPUT_ROOT / "training_history.json"

TRAIN_LR_DIR = DATASET_ROOT / "train" / "lr"
TRAIN_HR_DIR = DATASET_ROOT / "train" / "hr"

VAL_LR_DIR = DATASET_ROOT / "val" / "lr"
VAL_HR_DIR = DATASET_ROOT / "val" / "hr"

BATCH_SIZE = 4
NUM_EPOCHS = 3
LEARNING_RATE = 1e-4

NUM_WORKERS = 0
DEVICE = torch.device("cpu")

SEED = 42


# ============================================================
# Reproducibility
# ============================================================

torch.manual_seed(SEED)


# ============================================================
# Dataset
# ============================================================

class SuperResolutionDataset(Dataset):
    """Dataset for paired 4-band LR and HR TIFF images."""

    def __init__(self, lr_dir, hr_dir):
        self.lr_dir = Path(lr_dir)
        self.hr_dir = Path(hr_dir)

        self.lr_files = sorted(self.lr_dir.glob("*.tif"))

        if not self.lr_files:
            raise RuntimeError(f"No LR TIFF files found in {self.lr_dir}")

        self.pairs = []

        for lr_path in self.lr_files:
            hr_path = self.hr_dir / lr_path.name.replace(
                "_10m.tif",
                "_05m.tif",
            )

            if not hr_path.exists():
                raise RuntimeError(
                    f"Missing HR pair for: {lr_path.name}"
                )

            self.pairs.append((lr_path, hr_path))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, index):
        lr_path, hr_path = self.pairs[index]

        with rasterio.open(lr_path) as src:
            lr = src.read().astype("float32")

        with rasterio.open(hr_path) as src:
            hr = src.read().astype("float32")

        lr = torch.from_numpy(lr)
        hr = torch.from_numpy(hr)

        return lr, hr


# ============================================================
# Validation
# ============================================================

def validate_model(model, dataloader, loss_function):
    model.eval()

    total_loss = 0.0
    total_samples = 0

    with torch.no_grad():
        for lr, hr in dataloader:
            lr = lr.to(DEVICE)
            hr = hr.to(DEVICE)

            prediction = model(lr)
            loss = loss_function(prediction, hr)

            batch_size = lr.size(0)

            total_loss += loss.item() * batch_size
            total_samples += batch_size

    return total_loss / total_samples


# ============================================================
# Main training
# ============================================================

def main():

    print("=" * 70)
    print("2× MULTISPECTRAL SUPER-RESOLUTION TRAINING")
    print("=" * 70)

    print(f"Device        : {DEVICE}")
    print(f"Batch size    : {BATCH_SIZE}")
    print(f"Epochs        : {NUM_EPOCHS}")
    print(f"Learning rate : {LEARNING_RATE}")
    print(f"CPU threads   : {torch.get_num_threads()}")

    # --------------------------------------------------------
    # Output directories
    # --------------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Datasets
    # --------------------------------------------------------

    train_dataset = SuperResolutionDataset(
        TRAIN_LR_DIR,
        TRAIN_HR_DIR,
    )

    val_dataset = SuperResolutionDataset(
        VAL_LR_DIR,
        VAL_HR_DIR,
    )

    print()
    print(f"Training samples   : {len(train_dataset)}")
    print(f"Validation samples : {len(val_dataset)}")

    # --------------------------------------------------------
    # Data loaders
    # --------------------------------------------------------

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
    )

    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    model = SuperResolutionCNN().to(DEVICE)

    total_parameters = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print(f"Model parameters : {total_parameters}")

    # --------------------------------------------------------
    # Loss and optimizer
    # --------------------------------------------------------

    loss_function = nn.L1Loss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=LEARNING_RATE,
    )

    # --------------------------------------------------------
    # Training history
    # --------------------------------------------------------

    history = {
        "train_loss": [],
        "val_loss": [],
    }

    best_val_loss = float("inf")

    # --------------------------------------------------------
    # Training loop
    # --------------------------------------------------------

    for epoch in range(NUM_EPOCHS):

        model.train()

        running_loss = 0.0
        total_samples = 0

        for lr, hr in train_loader:

            lr = lr.to(DEVICE)
            hr = hr.to(DEVICE)

            optimizer.zero_grad()

            prediction = model(lr)

            loss = loss_function(
                prediction,
                hr,
            )

            loss.backward()

            optimizer.step()

            batch_size = lr.size(0)

            running_loss += loss.item() * batch_size
            total_samples += batch_size

        train_loss = running_loss / total_samples

        val_loss = validate_model(
            model,
            val_loader,
            loss_function,
        )

        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)

        print(
            f"Epoch {epoch + 1:02d}/{NUM_EPOCHS} | "
            f"Train Loss: {train_loss:.6f} | "
            f"Val Loss: {val_loss:.6f}"
        )

        # ----------------------------------------------------
        # Save best model
        # ----------------------------------------------------

        if val_loss < best_val_loss:

            best_val_loss = val_loss

            best_model_path = MODEL_DIR / "best_model.pth"

            torch.save(
                {
                    "epoch": epoch + 1,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "train_loss": train_loss,
                    "val_loss": val_loss,
                },
                best_model_path,
            )

            print(
                f"  → Best model saved "
                f"(val loss: {val_loss:.6f})"
            )

    # --------------------------------------------------------
    # Save training history
    # --------------------------------------------------------

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)

    print()
    print("=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"Best validation loss : {best_val_loss:.6f}")
    print(f"Best model           : {MODEL_DIR / 'best_model.pth'}")
    print(f"Training history     : {HISTORY_FILE}")


if __name__ == "__main__":
    main()