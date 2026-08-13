"""
segmentation.py — Phase 4: Rule-based customer segmentation.

SEGMENTS (explicit rules, traceable):
  S1 High-Value Loyal:          high_value_flag=1 AND loyalty_tier_B=High AND promo_flag=0
  S2 Promo-Dependent Buyers:    promo_flag=1 AND purchase_amount < median AND previous_purchases < median
  S3 Emerging Loyalists:        subscription_status=1 AND previous_purchases >= median AND promo_flag=0
  S4 Promo-Habituated Spenders: promo_flag=1 AND high_value_flag=1
  S5 Low-Value Occasional:      low_value_flag=1 AND low_repeat_flag=1
  S0 General Buyers:            all remaining unclassified rows

Priority order: S1 > S3 > S4 > S2 > S5 > S0
(Higher-value segments assigned first to avoid overlap)
"""
import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_PATH  = os.path.join(BASE_DIR, "data", "processed", "feature_table.csv")
CLT_PATH = os.path.join(BASE_DIR, "outputs", "customer_level_table.csv")
SEG_PATH = os.path.join(BASE_DIR, "outputs", "segment_summary.csv")

SEGMENT_LABELS = {
    "S1": "High-Value Loyal",
    "S2": "Promo-Dependent Buyers",
    "S3": "Emerging Loyalists",
    "S4": "Promo-Habituated Spenders",
    "S5": "Low-Value Occasional",
    "S0": "General Buyers",
}

def assign_segments(df):
    med_pa = df["purchase_amount"].median()
    med_pp = df["previous_purchases"].median()

    seg = pd.Series("S0", index=df.index)

    # S5 first (lowest priority base)
    m5 = (df["low_value_flag"] == 1) & (df["low_repeat_flag"] == 1)
    seg[m5] = "S5"

    # S2
    m2 = (df["promo_flag"] == 1) & (df["purchase_amount"] < med_pa) & (df["previous_purchases"] < med_pp)
    seg[m2] = "S2"

    # S4
    m4 = (df["promo_flag"] == 1) & (df["high_value_flag"] == 1)
    seg[m4] = "S4"

    # S3
    m3 = (df["subscription_status"] == 1) & (df["previous_purchases"] >= med_pp) & (df["promo_flag"] == 0)
    seg[m3] = "S3"

    # S1 (highest priority, overwrites)
    m1 = (df["high_value_flag"] == 1) & (df["loyalty_tier_B"] == "High") & (df["promo_flag"] == 0)
    seg[m1] = "S1"

    return seg

def build_segment_summary(df):
    rows = []
    for code, label in SEGMENT_LABELS.items():
        mask = df["segment_code"] == code
        sub  = df[mask]
        if len(sub) == 0:
            continue
        top_geo   = sub["location"].value_counts().head(3).index.tolist()
        top_cat   = sub["category"].value_counts().head(2).index.tolist()
        top_age   = sub["age_band"].value_counts().idxmax() if len(sub) > 0 else "N/A"
        top_gender= sub["gender"].value_counts().idxmax() if len(sub) > 0 else "N/A"
        rows.append({
            "segment_code":       code,
            "segment_label":      label,
            "count":              len(sub),
            "pct_of_total":       round(100 * len(sub) / len(df), 1),
            "avg_purchase_amount":round(sub["purchase_amount"].mean(), 2),
            "avg_previous_purchases": round(sub["previous_purchases"].mean(), 2),
            "avg_review_rating":  round(sub["review_rating"].mean(), 2),
            "avg_loyalty_score_A":round(sub["loyalty_score_A"].mean(), 3),
            "avg_loyalty_score_B":round(sub["loyalty_score_B"].mean(), 3),
            "pct_discount":       round(100 * sub["discount_applied"].mean(), 1),
            "pct_promo":          round(100 * sub["promo_code_used"].mean(), 1),
            "pct_subscribed":     round(100 * sub["subscription_status"].mean(), 1),
            "avg_purchases_per_year": round(sub["purchases_per_year"].mean(), 1),
            "avg_spend_x_freq":   round(sub["spend_x_frequency"].mean(), 1),
            "top_geographies":    ", ".join(top_geo),
            "top_categories":     ", ".join(top_cat),
            "modal_age_band":     str(top_age),
            "modal_gender":       top_gender,
        })
    return pd.DataFrame(rows)

def run_segmentation(in_path=IN_PATH, clt_path=CLT_PATH, seg_path=SEG_PATH):
    print("=" * 60)
    print("PHASE 4 — CUSTOMER SEGMENTATION")
    print("=" * 60)

    df = pd.read_csv(in_path)
    print(f"[LOAD] Feature table rows: {len(df):,}")

    # Assign segments
    df["segment_code"]  = assign_segments(df)
    df["segment_label"] = df["segment_code"].map(SEGMENT_LABELS)

    # Print distribution
    dist = df["segment_code"].value_counts().sort_index()
    print("\n[SEGMENTS] Distribution:")
    for code in dist.index:
        label = SEGMENT_LABELS[code]
        n     = dist[code]
        pct   = 100 * n / len(df)
        print(f"  {code} {label:30s} {n:5d} ({pct:5.1f}%)")

    # Segment summary
    summary = build_segment_summary(df)
    print("\n[SUMMARY] Segment profiles:")
    print(summary[["segment_label","count","avg_purchase_amount",
                    "avg_previous_purchases","pct_discount","avg_loyalty_score_B"]].to_string(index=False))

    # Business action map
    actions = {
        "S1": "Reward with exclusive access; no discount needed; upsell premium lines",
        "S2": "Test discount reduction in 10% cohort; shift to loyalty rewards",
        "S3": "Nurture with personalization; expand category breadth; reduce promo reliance",
        "S4": "Phase out discount slowly; test value messaging; monitor retention",
        "S5": "Re-engagement campaigns; evaluate acquisition cost vs LTV",
        "S0": "Standard marketing; collect more behavioral data",
    }
    print("\n[ACTIONS] Recommended business actions by segment:")
    for code, action in actions.items():
        print(f"  {code}: {action}")

    # Export
    os.makedirs(os.path.dirname(clt_path), exist_ok=True)
    df.to_csv(clt_path, index=False)
    summary.to_csv(seg_path, index=False)
    print(f"\n[EXPORT] Customer level table → {clt_path}")
    print(f"[EXPORT] Segment summary      → {seg_path}")
    print("=" * 60)
    return df, summary

if __name__ == "__main__":
    run_segmentation()
