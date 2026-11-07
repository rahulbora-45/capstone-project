# Satellite Image Processing and Analysis — Capstone Project

## Overview

This repository contains the development work for a capstone project focused on **satellite image processing and multispectral super-resolution**.

The project works with paired satellite imagery at different spatial resolutions and follows a structured, reproducible pipeline covering data extraction, verification, quality auditing, preprocessing, dataset preparation, model development, training, and evaluation.

The final machine learning task is **2× multispectral super-resolution**:

- Input: 4-band B, G, R, NIR satellite image
- Input resolution: 10 m
- Input size: `128 × 128`
- Target: 4-band B, G, R, NIR reference image
- Target resolution: 5 m
- Target size: `256 × 256`
- Scale factor: 2×

The objective is to generate high-resolution multispectral imagery while preserving **spectral and radiometric fidelity** for downstream applications such as land cover classification and NDVI analysis.

The original satellite data is preserved separately from all generated and processed data.

---

## Project Workflow

The project follows this workflow:

```text
Raw Satellite Data

        ↓

Data Extraction

        ↓

Data Verification

        ↓

Data Quality Audit

        ↓

Data Preprocessing

        ↓

Dataset Preparation

        ↓

Model Development

        ↓

Model Training

        ↓

Model Evaluation

        ↓

Final Analysis
```

### Current Progress

| Phase | Status |
|---|---|
| Project Setup | ✅ Completed |
| Data Extraction | ✅ Completed |
| Data Verification | ✅ Completed |
| Data Quality Audit | ✅ Completed |
| Data Preprocessing | ✅ Completed |
| Dataset Preparation | ✅ Completed |
| Model Development | ✅ Completed |
| Model Training | ⏳ Pending |
| Model Evaluation | ⏳ Pending |
| Final Analysis | ⏳ Pending |
| Documentation & Finalization | ⏳ Pending |

---

## Repository Structure

```text
Capstone-Project/

│
├── data/
│   ├── raw/                 # Original source data — do not modify
│   ├── extracted/           # Extracted satellite imagery
│   ├── processed/           # Generated preprocessing outputs
│   └── prepared/            # Model-ready datasets and split metadata

│
├── src/
│   ├── preprocessing/       # Data preprocessing and dataset preparation
│   ├── models/              # Model implementations and training/evaluation scripts
│   ├── training/             # Model training
│   └── evaluation/           # Model evaluation

│
├── scripts/                 # Utility, inspection, verification and audit scripts

│
├── tests/                   # Project tests

│
├── results/
│   ├── audit/               # Audit results
│   ├── model_training/      # Training history and model checkpoints
│   ├── model_evaluation/    # Test evaluation and prediction inspection
│   └── visualizations/      # Generated visualizations

│
├── experiments/             # Experimental work
├── notebooks/               # Analysis notebooks
├── configs/                 # Project configuration files

│
├── PROJECT_ROADMAP.md       # Project roadmap
├── PHASE_TRACKER.md         # Phase progress tracking
├── TASK_TRACKER.md          # Task tracking
├── TIMELINE.md              # Project timeline
├── CHANGELOG.md             # Project changes
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## Data Handling Principle

The original satellite data must remain unchanged.

The project follows a separate-data principle:

```text
data/raw
    │
    │ read only
    ▼
data/extracted
    │
    ▼
src/preprocessing
    │
    ├──→ data/processed
    │
    └──→ data/prepared
```

Preprocessing and dataset preparation operations generate new outputs rather than modifying the original source data.

---

## Data Audit

Before beginning preprocessing, the extracted satellite data was subjected to a quality and consistency audit.

The audit included checks related to:

- TIFF readability
- Dataset-level file validation
- Band availability
- Pixel statistics
- Scale and offset metadata
- Negative and zero pixel values
- Neighborhood inspection
- 10 m / 5 m data relationships
- Pair metadata
- Alignment-related checks
- Extraction verification

The completed audit checkpoint was committed to Git with:

```text
b07e380 Complete data audit and validation
```

---

# Data Preprocessing

The data preprocessing phase has been completed as a reproducible pipeline while preserving the original extracted satellite data.

## Preprocessing Strategy

- The original 10 m imagery is used as the reference spatial grid.
- The 5 m imagery is resampled to the 10 m resolution.
- Bilinear resampling is used for the 5 m to 10 m conversion.
- Original files under `data/extracted/` are not modified.
- Generated preprocessing outputs are stored under `data/processed/`.
- Processed raster data is stored as `float32`.

## 5 m to 10 m Resampling

The 5 m imagery was resampled to match the corresponding 10 m imagery in:

- Spatial dimensions
- Resolution
- CRS
- Transform
- Bounds

A total of **2,312 paired images** were processed successfully.

Validation results:

- Expected processed files: 2,312
- Actual processed files: 2,312
- Validation passed: 2,312
- Validation failed: 0

## 8-Channel Representation

An 8-channel intermediate representation was created during preprocessing.

The channels are organized as:

- Channels 1–4: Original 10 m B, G, R, NIR imagery
- Channels 5–8: Resampled 5 m B, G, R, NIR imagery at 10 m resolution

Each output:

- Contains 8 channels
- Uses `float32`
- Uses the 10 m spatial grid
- Preserves spatial alignment between the original 10 m and resampled 5 m data

A total of **2,312 8-channel outputs** were created.

Full validation results:

- Expected 8-channel files: 2,312
- Actual 8-channel files: 2,312
- Validation passed: 2,312
- Validation failed: 0
- Output bands validated: 18,496

The 8-channel representation is an **intermediate preprocessing representation**. The final super-resolution model operates on the original 4-band B, G, R, NIR input and predicts the corresponding 4-band high-resolution target.

## Preprocessing Validation

The preprocessing outputs were validated for:

- File count
- Band count
- Data type
- Spatial dimensions
- Resolution
- CRS
- Transform
- Bounds
- Channel correspondence with source imagery

The complete preprocessing dataset passed validation.

---

# Dataset Preparation

The Dataset Preparation phase has been completed.

The objective of this phase was to construct a leakage-safe, normalized, model-ready dataset for the final 2× multispectral super-resolution task.

## Final Model Data

The final model-ready dataset uses:

| Property | Low-Resolution Input | High-Resolution Target |
|---|---|---|
| Bands | B, G, R, NIR | B, G, R, NIR |
| Number of bands | 4 | 4 |
| Spatial resolution | 10 m | 5 m |
| Image size | `128 × 128` | `256 × 256` |
| Data type | `float32` | `float32` |
| Scale | — | 2× |

The LR and HR images are paired spatially and represent the same geographic area at different spatial resolutions.

## Dataset Split

A spatially grouped train/validation/test split was used to reduce the risk of spatial leakage.

The split was performed using spatial-index groups rather than randomly splitting individual image pairs.

Final split:

| Split | Spatial Groups | Pairs |
|---|---:|---:|
| Train | 224 | 1,583 |
| Validation | 48 | 351 |
| Test | 48 | 378 |
| **Total** | **320** | **2,312** |

No spatial-index leakage was detected between:

- Train and Validation
- Train and Test
- Validation and Test

Split manifests are stored under:

```text
data/prepared/splits/
```

with:

```text
train.csv
val.csv
test.csv
```

## Training Statistics

Training-only pixel statistics were calculated separately for the LR and HR training images.

The final dataset uses shared per-band training statistics for normalization.

Normalization is performed using:

```text
normalized = (pixel - mean) / standard_deviation
```

The shared statistics are:

| Band | Mean | Standard Deviation |
|---|---:|---:|
| B | 264.199009 | 234.576778 |
| G | 477.690158 | 268.662826 |
| R | 393.847771 | 377.589098 |
| NIR | 2351.310526 | 808.879710 |

The same normalization statistics are applied to both LR inputs and HR targets.

Negative pixel values are preserved and no clipping is applied in order to avoid unnecessarily altering the original radiometric information.

Normalization statistics are stored in:

```text
data/prepared/normalization/training_statistics.json
```

## Model-Ready Dataset

The final normalized dataset is stored under:

```text
data/prepared/dataset/
```

with the following structure:

```text
data/prepared/dataset/

│
├── train/
│   ├── lr/
│   └── hr/

│
├── val/
│   ├── lr/
│   └── hr/

│
└── test/
    ├── lr/
    └── hr/
```

Final dataset:

- Training pairs: 1,583
- Validation pairs: 351
- Test pairs: 378
- Total pairs: 2,312

## Dataset Preparation Validation

The complete model-ready dataset was validated for:

- File existence
- Pair integrity
- Train/validation/test split integrity
- Spatial leakage
- Band count
- Image dimensions
- Spatial resolution
- CRS
- Data type
- NaN and infinite values
- Normalization consistency
- Dataset completeness

Final validation result:

```text
Expected total pairs : 2312
Validation passed    : 2312
Validation failed    : 0

train : 1583/1583 passed
val   : 351/351 passed
test  : 378/378 passed

Spatial leakage: 0

MODEL-READY DATASET VALIDATION: PASS
```

The complete model-ready dataset was therefore ready for model development.

---

# Model Development

The Model Development phase has been completed as a working 4-band 2× multispectral super-resolution baseline.

## Model Architecture

A residual CNN was implemented in:

```text
src/models/super_resolution_cnn.py
```

The model uses:

- Input channels: 4
- Output channels: 4
- Input size: `128 × 128`
- Output size: `256 × 256`
- Feature channels: 64
- Residual blocks: 4
- Upsampling: PixelShuffle
- Scale factor: 2×
- Total parameters: **484,740**
- Trainable parameters: **484,740**

The architecture consists of:

```text
4-band 10 m LR image
        │
        ▼
Feature extraction
        │
        ▼
4 Residual Blocks
        │
        ▼
Feature refinement
        │
        ▼
PixelShuffle 2× upsampling
        │
        ▼
4-band 5 m HR prediction
```

The model was validated with both tensor input and real model-ready satellite imagery.

## Model Development Validation

### Shape Validation

```text
Input shape : (1, 4, 128, 128)
Output shape: (1, 4, 256, 256)
```

### Real Data Forward Pass

A real normalized LR satellite image was passed through the model successfully.

The prediction:

- Produced the expected `4 × 256 × 256` output
- Contained finite values
- Matched the required 2× spatial scale

### Real LR/HR Loss Validation

A real paired LR/HR sample was also used to verify the training objective.

```text
LR shape         : (1, 4, 128, 128)
HR shape         : (1, 4, 256, 256)
Prediction shape : (1, 4, 256, 256)
L1 loss          : 0.366234
```

The loss was finite and confirmed that the model can directly process the prepared training pairs.

## Model Training Pipeline

The training pipeline was implemented in:

```text
src/models/train_super_resolution.py
```

The training configuration uses:

- Loss function: L1 loss
- Optimizer: Adam
- Learning rate: `0.0001`
- Batch size: 4
- CPU execution
- CPU threads: 6
- Random seed: 42
- Best-model checkpointing based on validation loss

The training pipeline uses:

- Training pairs: 1,583
- Validation pairs: 351

The best checkpoint is stored at:

```text
results/model_training/models/best_model.pth
```

Training history is stored at:

```text
results/model_training/training_history.json
```

## Phase 7 Development Training Result

A 3-epoch model development run was completed.

| Epoch | Training Loss | Validation Loss |
|---|---:|---:|
| 1 | 0.238552 | 0.197748 |
| 2 | 0.189601 | 0.186061 |
| 3 | 0.183255 | **0.181112** |

The validation loss improved across all three epochs.

The best checkpoint was saved from:

```text
Epoch: 3
Validation L1 loss: 0.181112
```

This 3-epoch run is the completed Phase 7 development baseline. Further training experiments belong to the dedicated Model Training phase.

## Model Evaluation

The model evaluation pipeline was implemented in:

```text
src/models/evaluate_super_resolution.py
```

The complete held-out test set contains:

```text
378 test pairs
```

The evaluation includes:

- MAE
- RMSE
- PSNR
- SSIM
- Per-band metrics
- Original radiometric-space MAE
- Original radiometric-space RMSE
- Original radiometric-space PSNR

Final evaluation results are stored at:

```text
results/model_evaluation/test_evaluation.json
```

## Phase 7 Test Evaluation Results

### Normalized-Space Metrics

| Metric | Result |
|---|---:|
| MAE | **0.187928** |
| RMSE | **0.272454** |
| PSNR | **31.8522 dB** |
| SSIM | **0.817167** |

### Original Radiometric-Space Metrics

| Metric | Result |
|---|---:|
| MAE | **77.503309** |
| RMSE | **121.966275** |
| PSNR | **31.6207 dB** |

### Per-Band Normalized Metrics

| Band | MAE | RMSE | SSIM |
|---|---:|---:|---:|
| B | 0.203909 | 0.291385 | 0.775092 |
| G | 0.199023 | 0.285346 | 0.794277 |
| R | 0.170214 | 0.258539 | 0.816827 |
| NIR | 0.178568 | 0.241764 | 0.882472 |

### Per-Band Original Radiometric Metrics

| Band | MAE | RMSE |
|---|---:|---:|
| B | 47.832222 | 68.352109 |
| G | 53.470048 | 76.661730 |
| R | 64.271125 | 97.621673 |
| NIR | 144.439840 | 195.558233 |

## Prediction Inspection

A held-out test prediction was also inspected using:

```text
src/models/inspect_super_resolution_prediction.py
```

The inspected prediction achieved:

```text
MAE  : 0.140283
RMSE : 0.231572
```

Per-band MAE:

| Band | MAE |
|---|---:|
| B | 0.153984 |
| G | 0.143773 |
| R | 0.130944 |
| NIR | 0.132429 |

The inspected prediction was saved as:

```text
results/model_evaluation/prediction_inspection/prediction_4band.tif
```

Associated metrics were saved as:

```text
results/model_evaluation/prediction_inspection/prediction_metrics.json
```

## Model Development Files

The main Phase 7 model files are:

```text
src/models/
├── super_resolution_cnn.py
├── train_super_resolution.py
├── evaluate_super_resolution.py
└── inspect_super_resolution_prediction.py
```

Model outputs:

```text
results/
├── model_training/
│   ├── models/
│   │   └── best_model.pth
│   └── training_history.json
│
└── model_evaluation/
    ├── test_evaluation.json
    └── prediction_inspection/
        ├── prediction_4band.tif
        └── prediction_metrics.json
```

## Phase 7 Milestone

**Model Development is completed.**

The project now has a validated baseline model that accepts:

```text
4-band B, G, R, NIR
10 m resolution
128 × 128
```

and predicts:

```text
4-band B, G, R, NIR
5 m resolution
256 × 256
```

using 2× super-resolution.

The current best development checkpoint is:

```text
results/model_training/models/best_model.pth
```

The model is ready for the dedicated Model Training phase.

---

# Final Machine Learning Task

The final machine learning task is **2× multispectral image super-resolution**.

The model will receive:

```text
4-band B, G, R, NIR
10 m resolution
128 × 128
```

and predict:

```text
4-band B, G, R, NIR
5 m resolution
256 × 256
```

Conceptually:

```text
10 m LR Image

4 × 128 × 128

       │
       ▼

Super-Resolution Model

       │
       ▼

5 m HR Image

4 × 256 × 256
```

The model development stage focused on learning the spatial and spectral relationship between the paired low-resolution and high-resolution imagery.

The output should preserve:

- Spatial detail
- Spectral relationships
- Radiometric fidelity

The resulting high-resolution imagery is intended to remain useful for downstream applications such as:

- Land cover classification
- NDVI analysis
- Multispectral image analysis
- Other remote-sensing workflows

---

# Development Environment

The project is developed using Python and a virtual environment.

Install the project dependencies with:

```bash
pip install -r requirements.txt
```

Activate the virtual environment before running project scripts.

### Windows

```bat
.venv\Scripts\activate
```

---

# Running Scripts

Project utility and audit scripts are located in:

```text
scripts/
```

Preprocessing and dataset preparation scripts are located in:

```text
src/preprocessing/
```

Model development scripts are located in:

```text
src/models/
```

For example:

```bat
python src/preprocessing/validate_model_ready_dataset.py
```

The model training and evaluation modules should be executed from the project root using Python module execution.

For example:

```bat
python -m src.models.train_super_resolution
```

and:

```bat
python -m src.models.evaluate_super_resolution
```

Individual preprocessing, model development, training, and evaluation scripts should be executed according to their documented purpose and in the appropriate pipeline order.

---

# Git Workflow

Development work is organized into checkpoints.

A typical workflow is:

```text
Make changes

    ↓

Run validation/tests

    ↓

Review git diff

    ↓

Stage relevant files

    ↓

Commit

    ↓

Push to GitHub
```

Only files related to the completed work should be included in each checkpoint.

Generated files, temporary files, raw data, virtual environments, and unrelated work should not be committed unless explicitly required.

---

# Project Status

**Current phase: Model Training**

The following stages have been completed:

- Project Setup
- Data Extraction
- Data Verification
- Data Quality Audit
- Data Preprocessing
- Dataset Preparation
- Model Development

The Model Development phase has been completed with a validated 4-band 2× multispectral super-resolution baseline.

The current best checkpoint is:

```text
results/model_training/models/best_model.pth
```

The next stage is the dedicated Model Training phase.

## Next Objective

Begin **Model Training** for the 2× multispectral super-resolution task using:

- 4-band B, G, R, NIR input
- `128 × 128` LR images
- 10 m spatial resolution
- `256 × 256` HR targets
- 5 m spatial resolution
- 2× super-resolution
- Spectral and radiometric fidelity as key objectives
- Training split: 1,583 pairs
- Validation split: 351 pairs
- Test split: 378 pairs

The objective of the next phase is to conduct the planned model training experiments using the validated model architecture and model-ready dataset.