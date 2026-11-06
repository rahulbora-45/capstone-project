# Satellite Image Processing and Analysis — Capstone Project

## Overview

This repository contains the development work for a capstone project focused on **satellite image processing and analysis**.

The project works with satellite imagery at different spatial resolutions and includes stages for data extraction, verification, quality auditing, preprocessing, model development, training, and evaluation.

The project is being developed as a structured and reproducible pipeline, with the original satellite data preserved separately from generated and processed data.

---

## Project Workflow

The project follows this general workflow:

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
| Dataset Preparation | ⏳ Pending |
| Model Development | ⏳ Pending |
| Model Training | ⏳ Pending |
| Model Evaluation | ⏳ Pending |
| Final Analysis | ⏳ Pending |

---

## Repository Structure

```text
Capstone-Project/
│
├── data/
│   ├── raw/                 # Original source data — do not modify
│   ├── extracted/           # Extracted satellite imagery
│   └── processed/        # Generated preprocessing outputs
│
├── src/
│   ├── processed/       # Data preprocessing pipeline
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
    ▼
data/processed
```

Preprocessing operations should generate new outputs rather than modifying the original source data.

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

## Preprocessing

The data preprocessing phase has been completed as a reproducible pipeline while preserving the original extracted satellite data.

### Preprocessing Strategy

- The original 10m imagery is used as the reference spatial grid.
- The 5m imagery is resampled to the 10m resolution.
- Bilinear resampling is used for the 5m to 10m conversion.
- Original files under `data/extracted/` are not modified.
- Generated preprocessing outputs are stored under `data/processed/`.
- Processed raster data is stored as `float32`.

### 5m to 10m Resampling

The 5m imagery was resampled to match the corresponding 10m imagery in:

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

### 8-Channel Representation

A final 8-channel representation was created for model development.

The channels are organized as:

- Channels 1–4: Original 10m imagery
- Channels 5–8: Resampled 5m imagery at 10m resolution

Each output:

- Contains 8 channels
- Uses `float32`
- Uses the 10m spatial grid
- Preserves the spatial alignment between the original 10m and resampled 5m data

A total of **2,312 8-channel outputs** were created.

Full validation results:

- Expected 8-channel files: 2,312
- Actual 8-channel files: 2,312
- Validation passed: 2,312
- Validation failed: 0
- Output bands validated as `float32`: 18,496

### Preprocessing Validation

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

The complete 8-channel dataset passed validation.

Normalization/scaling, tiling, dataset splitting, and other model-training-specific preparation will be handled during the **Dataset Preparation** phase.

## Development Environment

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

## Running Scripts

Project utility and audit scripts are located in:

```text
scripts/
```

For example:

```bat
python scripts/audit_all_datasets.py
```

The preprocessing pipeline will be added under:

```text
src/preprocessing/
```

as the preprocessing phase is implemented.

---

## Git Workflow

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

## Project Status
**Current phase: Dataset Preparation**

The data extraction, verification, quality audit, and preprocessing stages have been completed. The next objective is to prepare the validated 8-channel data for dataset construction and model development.
---


Capstone Project — Satellite Image Processing and Analysis
