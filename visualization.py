"""
visualization.py — Phase 6: Generate all charts and dashboard-ready exports.
Saves PNG figures to outputs/figures/ and exports dashboard_data.csv.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import os
import warnings
warnings.filterwarnings("ignore")

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLT_PATH  = os.path.join(BASE_DIR, "outputs", "customer_level_table.csv")
SEG_PATH  = os.path.join(BASE_DIR, "outputs", "segment_summary.csv")
FIG_DIR   = os.path.join(BASE_DIR, "outputs", "figures")
DASH_PATH = os.path.join(BASE_DIR, "outputs", "dashboard_data.csv")

PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B", "#44BBA4"]
SEG_COLORS = {
    "S1":"#2E86AB","S2":"#C73E1D","S3":"#44BBA4",
    "S4":"#F18F01","S5":"#A23B72","S0":"#888888"
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 120,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})

def save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, f"{name}.png")
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  [FIG] Saved: {path}")

def fig1_value_pyramid(df, seg):
    """Panel 1: Customer value pyramid by segment"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Panel 1 — Customer Value Distribution", fontsize=15, fontweight="bold")

    # Left: Spend histogram with segment overlay
    ax = axes[0]
    ax.hist(df["purchase_amount"], bins=30, color="#2E86AB", alpha=0.7, edgecolor="white")
    ax.axvline(df["purchase_amount"].quantile(0.75), color="#C73E1D", linestyle="--",
               linewidth=1.5, label=f"Q75 = ${df['purchase_amount'].quantile(0.75):.0f}")
    ax.axvline(df["purchase_amount"].median(), color="#F18F01", linestyle="--",
               linewidth=1.5, label=f"Median = ${df['purchase_amount'].median():.0f}")
    ax.set_xlabel("Purchase Amount (USD)"); ax.set_ylabel("Count")
    ax.set_title("Spend Distribution")
    ax.legend(fontsize=9)

    # Right: Pyramid bar chart by segment
    ax2 = axes[1]
    seg_ord = seg.sort_values("avg_purchase_amount", ascending=True)
    bars = ax2.barh(seg_ord["segment_label"], seg_ord["avg_purchase_amount"],
                    color=[SEG_COLORS.get(c, "#888") for c in seg_ord["segment_code"]])
    for bar, val in zip(bars, seg_ord["avg_purchase_amount"]):
        ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f"${val:.0f}", va="center", fontsize=9)
    ax2.set_xlabel("Avg Purchase Amount (USD)")
    ax2.set_title("Avg Spend by Segment")
    plt.tight_layout()
    save(fig, "01_value_pyramid")

def fig2_promo_vs_loyalty(df, seg):
    """Panel 2: Promo dependency vs loyalty"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Panel 2 — Promo Dependency vs Loyalty", fontsize=15, fontweight="bold")

    # Left: scatter loyalty_A vs B coloured by promo flag
    ax = axes[0]
    colors = df["promo_flag"].map({1: "#C73E1D", 0: "#2E86AB"})
    ax.scatter(df["loyalty_score_A"], df["loyalty_score_B"],
               c=colors, alpha=0.25, s=15)
    ax.set_xlabel("Loyalty Score A (Behavioral)")
    ax.set_ylabel("Loyalty Score B (Commercial)")
    ax.set_title("Loyalty A vs B (red=promo user)")
    patch1 = mpatches.Patch(color="#C73E1D", label="Promo User")
    patch2 = mpatches.Patch(color="#2E86AB", label="Organic")
    ax.legend(handles=[patch1, patch2], fontsize=9)

    # Right: promo rate by segment
    ax2 = axes[1]
    seg_ord = seg.sort_values("pct_discount", ascending=True)
    colors2 = [SEG_COLORS.get(c, "#888") for c in seg_ord["segment_code"]]
    bars = ax2.barh(seg_ord["segment_label"], seg_ord["pct_discount"], color=colors2)
    for bar, val in zip(bars, seg_ord["pct_discount"]):
        ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                 f"{val:.0f}%", va="center", fontsize=9)
    ax2.set_xlabel("Discount Rate (%)")
    ax2.set_title("Discount Dependency by Segment")
    ax2.axvline(50, color="gray", linestyle="--", linewidth=1)
    plt.tight_layout()
    save(fig, "02_promo_vs_loyalty")

def fig3_geo_opportunity(df):
    """Panel 3: Geographic organic demand map (bar chart — no map API needed)"""
    geo = df.groupby("location").agg(
        n=("customer_id","count"),
        avg_spend=("purchase_amount","mean"),
        pct_organic=("promo_flag", lambda x: 100*(1-x.mean())),
        avg_loyalty=("loyalty_score_B","mean"),
    ).reset_index()
    geo = geo[geo["n"] >= 20].sort_values("pct_organic", ascending=False).head(20)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Panel 3 — Geographic Opportunity Analysis", fontsize=15, fontweight="bold")

    # Top organic states
    ax = axes[0]
    cmap = plt.cm.RdYlGn
    norm = plt.Normalize(geo["pct_organic"].min(), geo["pct_organic"].max())
    colors = [cmap(norm(v)) for v in geo["pct_organic"]]
    ax.barh(geo["location"], geo["pct_organic"], color=colors)
    ax.set_xlabel("% Organic (No Promo) Customers")
    ax.set_title("Top 20 States by Organic Demand Rate")
    ax.invert_yaxis()

    # Organic avg spend
    ax2 = axes[1]
    ax2.scatter(geo["pct_organic"], geo["avg_spend"], s=geo["n"]*0.5,
                c=geo["avg_loyalty"], cmap="viridis", alpha=0.8)
    for _, row in geo.iterrows():
        ax2.annotate(row["location"], (row["pct_organic"], row["avg_spend"]),
                     fontsize=7, alpha=0.7)
    ax2.set_xlabel("% Organic Demand"); ax2.set_ylabel("Avg Spend (USD)")
    ax2.set_title("Organic Rate vs Avg Spend\n(bubble size = customer count)")
    sm = plt.cm.ScalarMappable(cmap="viridis", norm=plt.Normalize(geo["avg_loyalty"].min(), geo["avg_loyalty"].max()))
    plt.colorbar(sm, ax=ax2, label="Avg Loyalty B")
    plt.tight_layout()
    save(fig, "03_geo_opportunity")

def fig4_category_funnel(df):
    """Panel 4: Category entry vs retention funnel"""
    cat = df.groupby("category").agg(
        n=("customer_id","count"),
        avg_spend=("purchase_amount","mean"),
        avg_repeats=("previous_purchases","mean"),
        avg_rating=("review_rating","mean"),
        pct_promo=("promo_flag",lambda x: 100*x.mean()),
    ).reset_index().sort_values("avg_repeats", ascending=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Panel 4 — Category Funnel (Entry vs Retention)", fontsize=15, fontweight="bold")

    ax = axes[0]
    colors3 = PALETTE[:len(cat)]
    bars = ax.bar(cat["category"], cat["avg_repeats"], color=colors3, edgecolor="white")
    ax.set_ylabel("Avg Previous Purchases (Repeat Proxy)")
    ax.set_title("Repeat Behavior by Category\n(higher = retention category)")
    ax.axhline(df["previous_purchases"].median(), color="gray",
               linestyle="--", linewidth=1.5, label=f"Median = {df['previous_purchases'].median():.0f}")
    ax.legend(fontsize=9)
    for bar, val in zip(bars, cat["avg_repeats"]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f"{val:.1f}", ha="center", fontsize=10)

    ax2 = axes[1]
    ax2.scatter(cat["avg_spend"], cat["avg_repeats"], s=cat["n"]*0.3,
                c=colors3[:len(cat)], alpha=0.9, zorder=3)
    for _, row in cat.iterrows():
        ax2.annotate(f"  {row['category']}", (row["avg_spend"], row["avg_repeats"]), fontsize=10)
    ax2.set_xlabel("Avg Spend (USD)"); ax2.set_ylabel("Avg Repeats")
    ax2.set_title("Spend vs Repeat by Category")
    plt.tight_layout()
    save(fig, "04_category_funnel")

def fig5_loyalty_comparison(df):
    """Loyalty A vs B comparison panels"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Loyalty Score Comparison: Definition A (Behavioral) vs B (Commercial)",
                 fontsize=14, fontweight="bold")

    # Score distributions
    for i, (col, label, ax) in enumerate(zip(
        ["loyalty_score_A","loyalty_score_B"],
        ["Score A (Behavioral)","Score B (Commercial)"],
        [axes[0,0], axes[0,1]]
    )):
        ax.hist(df[col], bins=40, color=PALETTE[i], alpha=0.8, edgecolor="white")
        ax.axvline(df[col].mean(), color="black", linestyle="--", linewidth=1.5,
                   label=f"Mean={df[col].mean():.2f}")
        ax.set_title(f"Distribution: {label}")
        ax.set_xlabel("Score (0–1)"); ax.legend(fontsize=9)

    # Spend by tier A
    spend_A = df.groupby("loyalty_tier_A", observed=True)["purchase_amount"].mean().reindex(["Low","Medium","High"])
    axes[1,0].bar(spend_A.index, spend_A.values, color=["#C73E1D","#F18F01","#2E86AB"])
    axes[1,0].set_title("Avg Spend by Loyalty Tier A")
    axes[1,0].set_ylabel("Avg Purchase Amount (USD)")
    for x, v in enumerate(spend_A.values):
        axes[1,0].text(x, v+0.5, f"${v:.0f}", ha="center", fontsize=10)

    # Spend by tier B
    spend_B = df.groupby("loyalty_tier_B", observed=True)["purchase_amount"].mean().reindex(["Low","Medium","High"])
    axes[1,1].bar(spend_B.index, spend_B.values, color=["#C73E1D","#F18F01","#44BBA4"])
    axes[1,1].set_title("Avg Spend by Loyalty Tier B")
    axes[1,1].set_ylabel("Avg Purchase Amount (USD)")
    for x, v in enumerate(spend_B.values):
        axes[1,1].text(x, v+0.5, f"${v:.0f}", ha="center", fontsize=10)

    plt.tight_layout()
    save(fig, "05_loyalty_comparison")

def fig6_segment_profiles(df, seg):
    """Radar-style segment profiles (bar grid)"""
    metrics = ["avg_purchase_amount","avg_previous_purchases","avg_review_rating",
               "pct_discount","avg_loyalty_score_B"]
    labels  = ["Avg Spend","Avg Repeats","Avg Rating","Discount %","Loyalty B"]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Segment Profile Comparison", fontsize=14, fontweight="bold")
    axes = axes.flatten()

    for i, (metric, label) in enumerate(zip(metrics, labels)):
        ax = axes[i]
        colors4 = [SEG_COLORS.get(c,"#888") for c in seg["segment_code"]]
        bars = ax.bar(seg["segment_code"], seg[metric], color=colors4)
        ax.set_title(label); ax.set_xlabel("Segment")
        for bar, val in zip(bars, seg[metric]):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                    f"{val:.1f}", ha="center", fontsize=8)

    # Legend panel
    axes[5].axis("off")
    legend_patches = [mpatches.Patch(color=SEG_COLORS[c], label=f"{c}: {lbl}")
                      for c, lbl in [
                          ("S1","High-Value Loyal"),("S2","Promo-Dependent"),
                          ("S3","Emerging Loyalists"),("S4","Promo-Habituated"),
                          ("S5","Low-Value Occasional"),("S0","General Buyers")]]
    axes[5].legend(handles=legend_patches, loc="center", fontsize=10, title="Segments")
    plt.tight_layout()
    save(fig, "06_segment_profiles")

def fig7_age_spend(df):
    """Age band analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Age Band Analysis", fontsize=14, fontweight="bold")

    age_data = df.groupby("age_band", observed=True).agg(
        n=("customer_id","count"),
        avg_spend=("purchase_amount","mean"),
        pct_promo=("promo_flag",lambda x: 100*x.mean()),
        avg_loyalty=("loyalty_score_B","mean"),
    ).reset_index()

    ax = axes[0]
    x = range(len(age_data))
    ax.bar(x, age_data["avg_spend"], color=PALETTE[:len(age_data)], alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(age_data["age_band"], rotation=15, ha="right")
    ax.set_ylabel("Avg Purchase Amount (USD)")
    ax.set_title("Avg Spend by Age Band")

    ax2 = axes[1]
    ax2.bar(x, age_data["pct_promo"], color=["#C73E1D"]*len(age_data), alpha=0.75)
    ax2.set_xticks(x); ax2.set_xticklabels(age_data["age_band"], rotation=15, ha="right")
    ax2.set_ylabel("% Using Promotions")
    ax2.set_title("Promo Dependence by Age Band")
    plt.tight_layout()
    save(fig, "07_age_analysis")

def fig8_founder_dashboard(df, seg):
    """4-panel founder dashboard — single figure"""
    fig = plt.figure(figsize=(20, 14), facecolor="#F8F9FA")
    fig.suptitle("D2C Fashion — Founder Customer Intelligence Dashboard",
                 fontsize=18, fontweight="bold", y=0.98, color="#1A1A2E")
    gs = GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    # Panel 1: Segment size pie
    ax1 = fig.add_subplot(gs[0, 0])
    seg_sorted = seg.sort_values("count", ascending=False)
    colors_p = [SEG_COLORS.get(c,"#888") for c in seg_sorted["segment_code"]]
    wedges, texts, autotexts = ax1.pie(
        seg_sorted["count"], labels=seg_sorted["segment_label"],
        autopct="%1.0f%%", colors=colors_p, startangle=90,
        textprops={"fontsize":8}, pctdistance=0.8)
    ax1.set_title("Customer Pyramid\n(by segment size)", fontweight="bold", pad=10)

    # Panel 2: Promo rate vs retention rate by segment
    ax2 = fig.add_subplot(gs[0, 1])
    colors_p2 = [SEG_COLORS.get(c,"#888") for c in seg["segment_code"]]
    scatter = ax2.scatter(seg["pct_discount"], seg["avg_previous_purchases"],
                          s=seg["count"]*0.5, c=colors_p2, alpha=0.9, zorder=3)
    for _, row in seg.iterrows():
        ax2.annotate(f"  {row['segment_code']}", (row["pct_discount"], row["avg_previous_purchases"]),
                     fontsize=9, fontweight="bold")
    ax2.set_xlabel("Discount Rate (%)"); ax2.set_ylabel("Avg Previous Purchases (Retention)")
    ax2.set_title("Promo Dependency vs Retention Rate\n(bubble=count)", fontweight="bold")
    ax2.axvline(50, color="gray", linestyle="--", linewidth=1, alpha=0.5)

    # Panel 3: Geographic Opportunity Map (Organic vs Spend)
    geo = df.groupby("location").agg(
        n=("customer_id","count"),
        pct_organic=("promo_flag", lambda x: 100*(1-x.mean())),
        avg_spend=("purchase_amount","mean"),
    ).reset_index()
    geo = geo[geo["n"] >= 15]
    ax3 = fig.add_subplot(gs[1, 0])
    scatter3 = ax3.scatter(geo["pct_organic"], geo["avg_spend"], s=geo["n"]*0.8,
                           c=geo["pct_organic"], cmap=plt.cm.RdYlGn, alpha=0.8, edgecolor="k")
    for _, row in geo.nlargest(8, "pct_organic").iterrows():
        ax3.annotate(f" {row['location']}", (row["pct_organic"], row["avg_spend"]), fontsize=8)
    for _, row in geo.nlargest(3, "avg_spend").iterrows():
        if row['location'] not in geo.nlargest(8, "pct_organic")["location"].values:
            ax3.annotate(f" {row['location']}", (row["pct_organic"], row["avg_spend"]), fontsize=8)
    ax3.set_xlabel("% Organic Buyers"); ax3.set_ylabel("Avg Spend (USD)")
    ax3.set_title("Geographic Opportunity Map\n(Spend vs Organic Demand)", fontweight="bold")

    # Panel 4: Category funnel
    cat = df.groupby("category").agg(
        avg_repeats=("previous_purchases","mean"),
        avg_spend=("purchase_amount","mean"),
    ).reset_index().sort_values("avg_repeats", ascending=False)
    ax4 = fig.add_subplot(gs[1, 1])
    colors_c = PALETTE[:len(cat)]
    bars4 = ax4.bar(cat["category"], cat["avg_repeats"], color=colors_c, edgecolor="white")
    ax4_twin = ax4.twinx()
    ax4_twin.plot(cat["category"], cat["avg_spend"], "o--", color="#1A1A2E",
                  linewidth=2, markersize=7, label="Avg Spend")
    ax4.set_ylabel("Avg Repeat Purchases"); ax4_twin.set_ylabel("Avg Spend (USD)")
    ax4.set_title("Category Funnel\n(bars=repeats, line=spend)", fontweight="bold")
    for bar in bars4:
        ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                 f"{bar.get_height():.0f}", ha="center", fontsize=9)
    save(fig, "00_founder_dashboard")

def export_dashboard_data(df):
    cols = [
        "customer_id","age","age_band","gender","category","season","location",
        "purchase_amount","previous_purchases","purchases_per_year","spend_x_frequency",
        "review_rating","subscription_status","discount_applied","promo_code_used",
        "promo_dependency_score","promo_flag","satisfaction_flag","high_satisfaction",
        "loyalty_score_A","loyalty_score_B","loyalty_tier_A","loyalty_tier_B",
        "high_value_flag","high_repeat_flag","segment_code","segment_label",
        "shipping_type","payment_method","premium_shipping","digital_payment",
    ]
    avail = [c for c in cols if c in df.columns]
    df[avail].to_csv(DASH_PATH, index=False)
    print(f"[EXPORT] Dashboard data → {DASH_PATH}")

def run_all():
    print("=" * 60)
    print("PHASE 6 — VISUALIZATION")
    print("=" * 60)
    df  = pd.read_csv(CLT_PATH)
    seg = pd.read_csv(SEG_PATH)
    print(f"[LOAD] {len(df):,} rows, {len(seg)} segments")

    fig1_value_pyramid(df, seg)
    fig2_promo_vs_loyalty(df, seg)
    fig3_geo_opportunity(df)
    fig4_category_funnel(df)
    fig5_loyalty_comparison(df)
    fig6_segment_profiles(df, seg)
    fig7_age_spend(df)
    fig8_founder_dashboard(df, seg)
    export_dashboard_data(df)

    print(f"\n[DONE] All charts saved to {FIG_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    run_all()
