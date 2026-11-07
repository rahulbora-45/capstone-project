# Phase Tracker

## Current Phase

**Phase 8 — Model Training**

**Status:** Pending

---

## Phase Status

| Phase | Status |
|---|---|
| Phase 1 — Project Setup | Completed |
| Phase 2 — Data Extraction | Completed |
| Phase 3 — Data Verification | Completed |
| Phase 4 — Data Quality Audit | Completed |
| Phase 5 — Data Preprocessing | Completed |
| Phase 6 — Dataset Preparation | Completed |
| Phase 7 — Model Development | Completed |
| Phase 8 — Model Training | Pending |
| Phase 9 — Model Evaluation | Pending |
| Phase 10 — Final Analysis | Pending |
| Phase 11 — Documentation & Finalization | Pending |

---

## Phase 5 — Data Preprocessing

**Status:** Completed

### Completed Work

- Inspected 10m and 5m raster structures.
- Validated individual 10m/5m image pairs.
- Validated 10m/5m pairing across the complete dataset.
- Confirmed 2,312/2,312 valid image pairs.
- Created and committed `src/preprocessing/pair_loader.py`.
- Implemented 5m → 10m resampling using bilinear interpolation.
- Used the original 10m imagery as the reference spatial grid.
- Processed all 2,312 valid image pairs successfully.
- Validated the complete resampled dataset:
  - Expected files: 2,312
  - Actual files: 2,312
  - Validation passed: 2,312
  - Validation failed: 0
- Created the final 8-channel representation:
  - Channels 1–4: original 10m imagery
  - Channels 5–8: resampled 5m imagery
  - Data type: `float32`
- Created 2,312 8-channel outputs.
- Validated the complete 8-channel dataset:
  - Expected files: 2,312
  - Actual files: 2,312
  - Validation passed: 2,312
  - Validation failed: 0
  - Validated output bands: 18,496
- Preserved the original data under `data/extracted/`.
- Stored generated preprocessing outputs under `data/processed/`.

### Preprocessing Validation

The complete preprocessing output passed structural and spatial validation.

Validation covered:

- File counts
- Band counts
- Data type
- Image dimensions
- Resolution
- CRS
- Transform
- Bounds
- Channel correspondence

### Phase 5 Milestone

**Data preprocessing is complete.**

The validated 8-channel dataset is ready for the Dataset Preparation phase.

---

## Phase 6 — Dataset Preparation

**Status:** Completed

### Completed Work

- Confirmed the extracted paired scenes are already model-ready spatial dimensions:
  - LR: 4-band B, G, R, NIR
  - LR: `128 × 128` at 10 m
  - HR: 4-band B, G, R, NIR
  - HR: `256 × 256` at 5 m
- Confirmed that additional tiling/cropping is not required.
- Created a spatially grouped train/validation/test split.
- Used spatial groups to prevent spatial leakage between dataset splits.
- Created:
  - Train: 224 spatial groups, 1,583 pairs
  - Validation: 48 spatial groups, 351 pairs
  - Test: 48 spatial groups, 378 pairs
- Confirmed zero spatial-index leakage between train, validation, and test sets.
- Created split manifests:
  - `data/prepared/splits/train.csv`
  - `data/prepared/splits/val.csv`
  - `data/prepared/splits/test.csv`
- Validated all split raster files:
  - Expected pairs: 2,312
  - Unique pairs: 2,312
  - Validation passed: 2,312
  - Validation failed: 0
- Calculated training-only pixel statistics for LR and HR data.
- Created shared per-band normalization statistics for B, G, R, and NIR.
- Used per-band standardization without clipping.
- Applied the same normalization statistics to both LR inputs and HR targets.
- Created the model-ready dataset under `data/prepared/dataset/`.
- Created:
  - 1,583 normalized training pairs
  - 351 normalized validation pairs
  - 378 normalized test pairs
- Preserved the original extracted data under `data/extracted/`.
- Validated the complete model-ready dataset:
  - Expected pairs: 2,312
  - Validation passed: 2,312
  - Validation failed: 0
- Confirmed all model-ready LR/HR files are `float32`.
- Confirmed LR shape is `4 × 128 × 128`.
- Confirmed HR shape is `4 × 256 × 256`.
- Confirmed LR resolution is 10 m.
- Confirmed HR resolution is 5 m.
- Confirmed normalized files contain only finite values.

### Dataset Preparation Validation

The complete dataset preparation pipeline passed validation.

Validation covered:

- Train/validation/test split counts
- Pair integrity
- Spatial leakage
- Band counts
- Image dimensions
- Resolution
- CRS
- Data type
- NaN/infinite values
- Normalization consistency
- Model-ready dataset completeness

Final validation result:

- Expected total pairs: **2,312**
- Validation passed: **2,312**
- Validation failed: **0**
- Spatial leakage: **0**
- Model-ready dataset validation: **PASS**

### Phase 6 Milestone

**Dataset preparation is complete.**

The validated model-ready LR/HR dataset is ready for the Model Development phase.

---

## Phase 7 — Model Development

**Status:** Completed

### Completed Work

- Defined the final machine learning task as 4-band multispectral 2× super-resolution.
- Confirmed the final model input:
  - 4-band B, G, R, NIR
  - 10 m spatial resolution
  - `128 × 128`
- Confirmed the final model target:
  - 4-band B, G, R, NIR
  - 5 m spatial resolution
  - `256 × 256`
- Confirmed the scale factor: **2×**.
- Designed and implemented a residual CNN super-resolution architecture.
- Created `src/models/super_resolution_cnn.py`.
- Implemented:
  - Initial feature extraction
  - Four residual blocks
  - Feature refinement
  - PixelShuffle 2× upsampling
  - Four-band output reconstruction
- Verified model input/output dimensions:
  - Input: `(1, 4, 128, 128)`
  - Output: `(1, 4, 256, 256)`
- Verified the model using a real normalized LR satellite image.
- Verified the model using a real LR/HR training pair.
- Confirmed finite model predictions and finite L1 loss.
- Created the model training pipeline:
  - `src/models/train_super_resolution.py`
- Configured the training pipeline to use:
  - L1 loss
  - Adam optimizer
  - CPU execution
  - Reproducible seed: 42
  - Best-model checkpointing based on validation loss
- Created the model evaluation pipeline:
  - `src/models/evaluate_super_resolution.py`
- Created prediction inspection:
  - `src/models/inspect_super_resolution_prediction.py`
- Trained the model for 3 epochs.
- Saved the best checkpoint:
  - `results/model_training/models/best_model.pth`
- Confirmed the best checkpoint was from epoch 3.
- Created training history:
  - `results/model_training/training_history.json`
- Evaluated the model on all 378 held-out test samples.
- Evaluated model performance in normalized space.
- Added original radiometric-space evaluation using the shared training normalization statistics.
- Preserved the normalized evaluation metrics while adding radiometric metrics.
- Saved final Phase 7 evaluation results:
  - `results/model_evaluation/test_evaluation.json`

### Model Architecture

The developed model contains:

- Input channels: 4
- Output channels: 4
- Feature channels: 64
- Residual blocks: 4
- Upscaling method: PixelShuffle
- Scale factor: 2×
- Total parameters: **484,740**
- Trainable parameters: **484,740**

### Phase 7 Training Result

The 3-epoch development run produced:

- Best checkpoint epoch: **3**
- Best validation L1 loss: **0.181112**

Training loss decreased across the three epochs, and validation loss also continued to improve:

| Epoch | Training Loss | Validation Loss |
|---|---:|---:|
| 1 | 0.238552 | 0.197748 |
| 2 | 0.189601 | 0.186061 |
| 3 | 0.183255 | **0.181112** |

### Phase 7 Test Evaluation

Evaluation was performed on the complete held-out test set of 378 samples.

#### Normalized-Space Metrics

| Metric | Result |
|---|---:|
| MAE | **0.187928** |
| RMSE | **0.272454** |
| PSNR | **31.8522 dB** |
| SSIM | **0.817167** |

#### Original Radiometric-Space Metrics

| Metric | Result |
|---|---:|
| MAE | **77.503309** |
| RMSE | **121.966275** |
| PSNR | **31.6207 dB** |

#### Per-Band Normalized Metrics

| Band | MAE | RMSE | SSIM |
|---|---:|---:|---:|
| B | 0.203909 | 0.291385 | 0.775092 |
| G | 0.199023 | 0.285346 | 0.794277 |
| R | 0.170214 | 0.258539 | 0.816827 |
| NIR | 0.178568 | 0.241764 | 0.882472 |

#### Per-Band Original Radiometric Metrics

| Band | MAE | RMSE |
|---|---:|---:|
| B | 47.832222 | 68.352109 |
| G | 53.470048 | 76.661730 |
| R | 64.271125 | 97.621673 |
| NIR | 144.439840 | 195.558233 |

### Phase 7 Validation

The model development pipeline was successfully validated through:

- Model architecture shape validation
- Real-data forward-pass validation
- Real LR/HR loss validation
- Training pipeline execution
- Validation-loss monitoring
- Best-checkpoint creation
- Complete test-set evaluation
- Normalized-space evaluation
- Original radiometric-space evaluation
- Per-band evaluation
- Prediction inspection

### Phase 7 Milestone

**Model development is complete.**

The project now has a working and evaluated 4-band 2× multispectral super-resolution baseline model.

The current best checkpoint is:

`results/model_training/models/best_model.pth`

The model is ready for the dedicated Model Training phase.

---

## Next Milestone

Begin **Phase 8 — Model Training**.

The Phase 8 objective is to conduct the planned model training experiments using the validated model architecture and model-ready dataset.

The training task remains:

- Input: 4-band B, G, R, NIR, 10 m, `128 × 128`
- Target: 4-band B, G, R, NIR, 5 m, `256 × 256`
- Scale factor: 2×
- Training split: 1,583 pairs
- Validation split: 351 pairs
- Test split: 378 pairs
- Objective: preserve spectral and radiometric fidelity for downstream applications such as land cover classification and NDVI analysis.