
from pathlib import Path
import pandas as pd
import rasterio

ROOT = Path(r"D:\Dataset\ANJI\ANJI")
INDEX = ROOT / "index.csv"

df = pd.read_csv(INDEX, sep="\t")

lr_col = "b2b3b4b8_10m"
hr_col = "b2b3b4b8_05m"

# Build a filename lookup from the extracted TIFFs.
lookup = {}
for p in ROOT.rglob("*.tif"):
    lookup.setdefault(p.name, []).append(p)

results = []

for row_number, row in df.iterrows():
    lr_name = Path(str(row[lr_col])).name
    hr_name = Path(str(row[hr_col])).name

    lr_matches = lookup.get(lr_name, [])
    hr_matches = lookup.get(hr_name, [])

    result = {
        "index_row": row_number,
        "lr_file": lr_name,
        "hr_file": hr_name,
        "status": "OK",
        "details": "",
    }

    if len(lr_matches) != 1 or len(hr_matches) != 1:
        result["status"] = "FILE_MISSING_OR_AMBIGUOUS"
        result["details"] = (
            f"LR matches={len(lr_matches)}, HR matches={len(hr_matches)}"
        )
        results.append(result)
        continue

    try:
        with rasterio.open(lr_matches[0]) as lr, \
             rasterio.open(hr_matches[0]) as hr:

            issues = []

            if lr.crs != hr.crs:
                issues.append("CRS mismatch")

            if lr.bounds != hr.bounds:
                issues.append("bounds mismatch")

            if (lr.width, lr.height) != (128, 128):
                issues.append("unexpected LR dimensions")

            if (hr.width, hr.height) != (256, 256):
                issues.append("unexpected HR dimensions")

            if lr.count != 4 or hr.count != 4:
                issues.append("unexpected band count")

            if abs(lr.res[0] / hr.res[0] - 2) > 1e-6:
                issues.append("x resolution ratio not 2")

            if abs(lr.res[1] / hr.res[1] - 2) > 1e-6:
                issues.append("y resolution ratio not 2")

            if lr.transform != hr.transform:
                # Different pixel sizes are expected; compare origins.
                if (
                    abs(lr.transform.c - hr.transform.c) > 1e-6
                    or abs(lr.transform.f - hr.transform.f) > 1e-6
                ):
                    issues.append("grid origins differ")

            if issues:
                result["status"] = "CHECK"
                result["details"] = "; ".join(issues)

    except Exception as exc:
        result["status"] = "READ_ERROR"
        result["details"] = repr(exc)

    results.append(result)

out = pd.DataFrame(results)
out_path = Path(r"D:\Capstone\pair_validation.csv")
out.to_csv(out_path, index=False)

print("Index rows:", len(df))
print("\nPair validation summary:")
print(out["status"].value_counts(dropna=False).to_string())
print("\nExamples needing attention:")
print(
    out.loc[out["status"] != "OK"]
    .head(20)
    .to_string(index=False)
)
print("\nSaved:", out_path)
