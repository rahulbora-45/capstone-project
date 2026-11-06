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
| Model Development | ⏳ Pending |
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
│   ├── models/              # Model implementations
│   ├── training/            # Model training
│   └── evaluation/          # Model evaluation
│
├── scripts/                 # Utility, inspection, verification and audit scripts
│
├── tests/                   # Project tests
│
├── results/
│   ├── audit/               # Audit results
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
    │  read only
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

The 8-channel representation is an **intermediate preprocessing representation**. The final super-resolution model will operate on the original 4-band B, G, R, NIR input and predict the corresponding 4-band high-resolution target.

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

The complete model-ready dataset is therefore ready for model development.

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

The model development stage will focus on learning the spatial and spectral relationship between the paired low-resolution and high-resolution imagery.

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

For example:

```bat
python src/preprocessing/validate_model_ready_dataset.py
```

Individual preprocessing and dataset preparation scripts should be executed according to their documented purpose and in the appropriate pipeline order.

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

**Current phase: Model Development**

The following stages have been completed:

- Project Setup
- Data Extraction
- Data Verification
- Data Quality Audit
- Data Preprocessing
- Dataset Preparation

The validated model-ready dataset is now available for the next stage.

## Next Objective

Begin **Model Development** for the 2× multispectral super-resolution task using:

- 4-band B, G, R, NIR input
- `128 × 128` LR images
- 10 m spatial resolution
- `256 × 256` HR targets
- 5 m spatial resolution
- 2× super-resolution
- Spectral and radiometric fidelity as key objectives