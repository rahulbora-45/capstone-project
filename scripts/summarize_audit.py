
import pandas as pd

bands = pd.read_csv("audit_band_stats.csv")
files = pd.read_csv("audit_file_summary.csv")

print("\n=== 1. Files by resolution group ===")
print(
    files.groupby("group").agg(
        files=("path", "count"),
        files_with_missing_crs=(
            "crs", lambda s: s.isna().sum() + (s.astype(str) == "None").sum()
        ),
        files_with_nodata_metadata=("nodata", lambda s: s.notna().sum()),
        files_with_invalid_mask=("all_masks_valid", lambda s: (~s).sum()),
    ).to_string()
)

print("\n=== 2. Negative values by resolution and band ===")
print(
    bands.groupby(["group", "band"]).agg(
        file_band_rows=("path", "count"),
        rows_with_negatives=("negative_count", lambda s: (s > 0).sum()),
        total_negative_pixels=("negative_count", "sum"),
        rows_with_zeros=("zero_count", lambda s: (s > 0).sum()),
        total_zero_pixels=("zero_count", "sum"),
        rows_with_invalid_mask_pixels=(
            "mask_invalid_count", lambda s: (s > 0).sum()
        ),
    ).to_string()
)

print("\n=== 3. File dimensions and band counts ===")
print(
    files.groupby(["group", "width", "height", "band_count"])
    .size()
    .rename("files")
    .to_string()
)

print("\n=== 4. File status counts ===")
print(files["status"].value_counts(dropna=False).to_string())

print("\n=== 5. Files with invalid masks ===")
invalid = files.loc[
    ~files["all_masks_valid"].astype(str).str.lower().eq("true"),
    ["path", "group", "all_masks_valid", "status"]
]
print("Count:", len(invalid))
if len(invalid):
    print(invalid.head(20).to_string(index=False))

print("\n=== 6. Files with negative values in any band ===")
negative = bands.loc[bands["negative_count"] > 0]
print("File-band rows:", len(negative))
print("Distinct files:", negative["path"].nunique())
