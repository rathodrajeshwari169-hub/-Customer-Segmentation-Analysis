"""
feature_engineering.py — Phase 3: Build analytical features from cleaned data.

PROXIES DOCUMENTED:
  spend_x_frequency: purchase_amount * purchases_per_year (annualised value proxy)
  loyalty_score_A: behavioral (prev_purchases + subscription + frequency + rating)
  loyalty_score_B: commercial (spend + prev_purchases + (1-promo) + rating)
  promo_dependency_score: avg of discount_applied and promo_code_used (0, 0.5, or 1)
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH  = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
OUT_PATH = os.path.join(BASE_DIR, "data", "processed", "feature_table.csv")

def minmax(s):
    rng = s.max() - s.min()
    return (s - s.min()) / rng if rng > 0 else s * 0.0

def engineer_features(in_path=IN_PATH, out_path=OUT_PATH):
    print("=" * 60)
    print("PHASE 3 — FEATURE ENGINEERING")
    print("=" * 60)
    df = pd.read_csv(in_path)
    print(f"[LOAD] Cleaned rows: {len(df):,}")

    # Value features
    df["spend_x_frequency"] = df["purchase_amount"] * df["purchases_per_year"]
    pa_q75 = df["purchase_amount"].quantile(0.75)
    pa_q25 = df["purchase_amount"].quantile(0.25)
    pp_q75 = df["previous_purchases"].quantile(0.75)
    pp_q25 = df["previous_purchases"].quantile(0.25)
    df["high_value_flag"]  = (df["purchase_amount"] >= pa_q75).astype(int)
    df["low_value_flag"]   = (df["purchase_amount"] <= pa_q25).astype(int)
    df["high_repeat_flag"] = (df["previous_purchases"] >= pp_q75).astype(int)
    df["low_repeat_flag"]  = (df["previous_purchases"] <= pp_q25).astype(int)
    print(f"[VALUE] PA Q25={pa_q25}, Q75={pa_q75} | PP Q25={pp_q25}, Q75={pp_q75}")

    # Promo features
    df["promo_dependency_score"] = (df["discount_applied"] + df["promo_code_used"]) / 2.0
    df["promo_flag"] = (df["promo_dependency_score"] > 0).astype(int)
    print(f"[PROMO] promo_flag count: {df['promo_flag'].sum():,}")

    # Satisfaction
    df["satisfaction_flag"] = (df["review_rating"] >= 4.0).astype(int)
    df["high_satisfaction"] = (df["review_rating"] >= 4.5).astype(int)
    df["low_satisfaction"]  = (df["review_rating"] < 3.0).astype(int)

    # Age bands
    df["age_band"] = pd.cut(df["age"],
        bins=[17, 24, 34, 49, 70],
        labels=["Teen (18-24)", "Young Adult (25-34)", "Mid-Age (35-49)", "Senior (50-70)"])
    print(f"[AGE]\n{df['age_band'].value_counts().to_string()}")

    # Loyalty Score A — Behavioral
    norm_prev   = minmax(df["previous_purchases"])
    norm_freq   = minmax(df["purchases_per_year"])
    norm_rating = minmax(df["review_rating"])
    sub_score   = df["subscription_status"].astype(float)
    df["loyalty_score_A"] = (0.30*norm_prev + 0.25*sub_score + 0.25*norm_freq + 0.20*norm_rating)

    # Loyalty Score B — Commercial
    norm_spend = minmax(df["purchase_amount"])
    no_promo   = 1.0 - df["promo_dependency_score"]
    df["loyalty_score_B"] = (0.35*norm_spend + 0.25*norm_prev + 0.25*no_promo + 0.15*norm_rating)

    # Loyalty tiers
    for score_col, tier_col in [("loyalty_score_A","loyalty_tier_A"),
                                  ("loyalty_score_B","loyalty_tier_B")]:
        q33 = df[score_col].quantile(0.33)
        q66 = df[score_col].quantile(0.66)
        df[tier_col] = pd.cut(df[score_col], bins=[-np.inf, q33, q66, np.inf],
                               labels=["Low","Medium","High"])

    # Comparison summary
    corr = df["loyalty_score_A"].corr(df["loyalty_score_B"])
    agree = (df["loyalty_tier_A"] == df["loyalty_tier_B"]).sum()
    print(f"\n[LOYALTY] Score A vs B correlation: {corr:.3f}")
    print(f"[LOYALTY] Tier agreement: {agree}/{len(df)} ({100*agree/len(df):.1f}%)")
    print("[LOYALTY A] Avg spend by tier:")
    print(df.groupby("loyalty_tier_A", observed=True)["purchase_amount"].mean().round(2).to_string())
    print("[LOYALTY B] Avg spend by tier:")
    print(df.groupby("loyalty_tier_B", observed=True)["purchase_amount"].mean().round(2).to_string())

    # Convenience features
    df["premium_shipping"] = df["shipping_type"].isin(
        ["Express","Next Day Air","2-Day Shipping"]).astype(int)
    df["digital_payment"] = df["payment_method"].isin(
        ["Venmo","Paypal","Debit Card","Credit Card"]).astype(int)
    df["category_code"] = df["category"].astype("category").cat.codes

    # Export
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"\n[EXPORT] Feature table → {out_path} | Shape: {df.shape}")
    print("=" * 60)
    return df

if __name__ == "__main__":
    engineer_features()
