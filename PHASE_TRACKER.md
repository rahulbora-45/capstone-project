# Phase Tracker

## Current Phase

**Phase 7 — Model Development**

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
| Phase 7 — Model Development | Pending |
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

## Next Milestone

Begin Model Development for the 2× multispectral super-resolution task.

The model will use:

- Input: 4-band B, G, R, NIR, 10 m, `128 × 128`
- Target: 4-band B, G, R, NIR, 5 m, `256 × 256`
- Scale factor: 2×
- Objective: preserve spectral and radiometric fidelity for downstream applications such as land cover classification and NDVI analysis.