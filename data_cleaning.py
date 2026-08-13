"""
data_cleaning.py
----------------
Phase 2: Load raw Dataset.csv, standardize, impute missing values,
and export a clean CSV ready for feature engineering.

ASSUMPTIONS DOCUMENTED:
- Each Customer ID is a unique transaction snapshot (no longitudinal data).
- Review Rating missing (~5%) → imputed with column MEDIAN (not mean, to be
  robust against the bimodal distribution observed in the data). Imputed rows
  flagged with review_imputed=1.
- Yes/No columns (Subscription Status, Discount Applied, Promo Code Used)
  converted to 1/0 integers.
- Frequency of Purchases mapped to a purchase-per-year numeric proxy.
- Structural note: rows 1-~1900 have Subscription/Discount/Promo = Yes (all);
  rows ~1901-3901 = No (all). This appears to be an assembly artifact from two
  source files. It is documented but NOT used to engineer artificial segments.
"""

import pandas as pd
import numpy as np
import os

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw", "Dataset.csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")


# ── Frequency → purchases-per-year proxy ─────────────────────────────────────
FREQ_MAP = {
    "Weekly": 52,
    "Fortnightly": 26,
    "Bi-Weekly": 26,          # same cadence as Fortnightly
    "Monthly": 12,
    "Quarterly": 4,
    "Every 3 Months": 4,      # same as Quarterly
    "Annually": 1,
}


def load_and_clean(raw_path: str = RAW_PATH, out_path: str = OUT_PATH) -> pd.DataFrame:
    print("=" * 60)
    print("PHASE 2 — DATA CLEANING")
    print("=" * 60)

    # ── 1. Load ───────────────────────────────────────────────────────────────
    df = pd.read_csv(raw_path)
    print(f"\n[LOAD] Raw rows: {len(df):,}  |  Columns: {df.shape[1]}")

    # ── 2. Standardize column names ───────────────────────────────────────────
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[\s\(\)/]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    # Manual renames for clarity
    df.rename(columns={
        "customer_id": "customer_id",
        "purchase_amount_usd": "purchase_amount",
        "review_rating": "review_rating",
        "subscription_status": "subscription_status",
        "discount_applied": "discount_applied",
        "promo_code_used": "promo_code_used",
        "previous_purchases": "previous_purchases",
        "payment_method": "payment_method",
        "frequency_of_purchases": "frequency_of_purchases",
        "item_purchased": "item_purchased",
        "shipping_type": "shipping_type",
    }, inplace=True)

    print(f"[COLS] Standardized: {list(df.columns)}")

    # ── 3. Check duplicates ───────────────────────────────────────────────────
    n_dup = df.duplicated(subset="customer_id").sum()
    print(f"[DEDUP] Duplicate customer_ids: {n_dup}")

    # ── 4. Missing values audit ────────────────────────────────────────────────
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    print(f"\n[MISSING]\n{missing.to_string()}")

    # ── 5. Impute Review Rating ───────────────────────────────────────────────
    # ASSUMPTION: median imputation chosen over mean to resist outlier pull.
    # Imputed rows flagged with review_imputed=1.
    df["review_imputed"] = df["review_rating"].isnull().astype(int)
    median_rating = df["review_rating"].median()
    df["review_rating"] = df["review_rating"].fillna(median_rating)
    n_imputed = df["review_imputed"].sum()
    print(f"\n[IMPUTE] Review Rating median = {median_rating:.2f} | "
          f"Rows imputed: {n_imputed} ({100*n_imputed/len(df):.1f}%)")

    # ── 6. Binary encode Yes/No columns ──────────────────────────────────────
    yn_cols = ["subscription_status", "discount_applied", "promo_code_used"]
    for col in yn_cols:
        df[col] = df[col].map({"Yes": 1, "No": 0})
    print(f"[ENCODE] Binary encoded: {yn_cols}")

    # ── 7. Frequency → numeric ────────────────────────────────────────────────
    df["purchases_per_year"] = df["frequency_of_purchases"].map(FREQ_MAP)
    unmapped = df["purchases_per_year"].isnull().sum()
    if unmapped > 0:
        print(f"[WARN] {unmapped} rows with unmapped frequency → set to median")
        df["purchases_per_year"] = df["purchases_per_year"].fillna(
            df["purchases_per_year"].median()
        )
    print(f"[FREQ] purchases_per_year distribution:\n"
          f"{df['purchases_per_year'].value_counts().sort_index().to_string()}")

    # ── 8. Structural split flag ──────────────────────────────────────────────
    # NOTE: The dataset was apparently assembled from two sources.
    # First ~1,900 rows = all Yes (subscription/discount/promo).
    # Remaining rows = all No. Flagged here for awareness, not for segmentation.
    df["dataset_block"] = df["subscription_status"].apply(
        lambda x: "promo_block" if x == 1 else "organic_block"
    )
    block_counts = df["dataset_block"].value_counts()
    print(f"\n[STRUCT] Dataset block distribution:\n{block_counts.to_string()}")
    print("  NOTE: This split likely reflects two source files assembled together.")
    print("  It will be accounted for in analysis but not used as a raw segment trigger.")

    # ── 9. Standardize categoricals ──────────────────────────────────────────
    cat_cols = ["gender", "category", "season", "size", "shipping_type",
                "payment_method", "location", "item_purchased"]
    for col in cat_cols:
        df[col] = df[col].str.strip().str.title()

    # ── 10. Type enforcement ─────────────────────────────────────────────────
    df["age"] = df["age"].astype(int)
    df["purchase_amount"] = df["purchase_amount"].astype(float)
    df["previous_purchases"] = df["previous_purchases"].astype(int)
    df["review_rating"] = df["review_rating"].astype(float)

    # ── 11. Summary stats ────────────────────────────────────────────────────
    print("\n[SUMMARY] Numeric columns:")
    print(df[["age", "purchase_amount", "previous_purchases",
              "review_rating", "purchases_per_year"]].describe().round(2).to_string())

    print("\n[SUMMARY] Categorical value counts:")
    for col in ["gender", "category", "season", "subscription_status",
                "discount_applied", "promo_code_used"]:
        print(f"\n  {col}:\n{df[col].value_counts().to_string()}")

    # ── 12. Export ────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\n[EXPORT] Cleaned data → {out_path}")
    print(f"         Shape: {df.shape}")
    print("=" * 60)

    return df


if __name__ == "__main__":
    load_and_clean()
