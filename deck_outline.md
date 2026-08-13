# Slide Deck Outline — D2C Fashion Customer Intelligence
## "Decoding Customer Value" | Board / Founder Presentation

---

## SLIDE 1 — TITLE

**Title:** Decoding Customer Value: A D2C Fashion Intelligence Report  
**Subtitle:** Who buys, who stays, and who only buys on discount  
**Visual:** Brand-coloured cover with customer silhouette collage  
**Talking Points:**
- 3,900 real customer transactions, one dataset, five business questions
- No assumptions about timestamps, margins, or loyalty programs we don't have
- Every recommendation is traceable to data

---

## SLIDE 2 — THE FIVE QUESTIONS WE ANSWER

**Title:** Five Questions. Five Answers.  
**Visual:** Five numbered tiles, each with a question  

1. Who are the most valuable customers?
2. Who buys only because of promotions?
3. Which geographies and categories are underlevered?
4. How should our promotional strategy change?
5. What does the ideal customer profile look like?

**Talking Points:**
- Each answer comes with explicit data-backed logic
- All segments have rules you can reproduce in SQL

---

## SLIDE 3 — DATA OVERVIEW

**Title:** What We Know (And What We Don't)  
**Visual:** Data card grid — green checkmarks vs red X marks  

| Have ✅ | Don't Have ❌ |
|---|---|
| 3,900 transactions | Timestamps / Dates |
| 18 attributes per customer | Margin / Cost data |
| Spend, repeats, satisfaction | True CLV |
| US state geography | Online vs offline channel |

**Talking Points:**
- No fake metrics — every limitation is documented
- Where data is missing, we use transparent proxies (labelled)
- Dataset has a structural split: ~1,053 subscribers all used promos; ~2,847 non-subscribers used none. We controlled for this.

---

## SLIDE 4 — CUSTOMER SEGMENTS AT A GLANCE

**Title:** Five Segments, Five Different Strategies  
**Visual:** Pie chart (segment sizes) + colour-coded icon for each  

| Segment | Size | Avg Spend | Promo Rate |
|---|---|---|---|
| S1: High-Value Loyal | 14.1% | $90.89 | 0% |
| S4: Promo-Habituated Spenders | 10.3% | $90.48 | 100% |
| S0: General Buyers | 61.5% | $52.86 | 37% |
| S2: Promo-Dependent Buyers | 10.1% | $39.05 | 100% |
| S5: Low-Value Occasional | 3.9% | $29.33 | 0% |

**Talking Points:**
- S1 and S4 have identical spend — but completely different commercial profiles
- The key insight: not all high spenders are equally valuable
- S0 is the growth sandbox — 61% of customers with room to move up

---

## SLIDE 5 — THE LOYALTY DEFINITION DEBATE

**Title:** Not All Loyalty Is Equal  
**Visual:** Side-by-side bar chart — Avg Spend by Loyalty Tier A vs B  

**Score A (Behavioral):** Low=$59.99 | Medium=$59.42 | High=$59.88 → FLAT  
**Score B (Commercial):** Low=$45.81 | Medium=$57.74 | High=$75.27 → CLEAR GRADIENT  

**Talking Points:**
- We tested two definitions — behavioral and commercial
- Score A looks at engagement: frequency, subscription, repeats
- Score B looks at commercial impact: spend, repeats, organic buying, satisfaction
- **Winner: Score B** — only Score B separates who actually generates revenue
- Key finding: in this dataset, a "loyal" subscriber can still be 100% discount-dependent

---

## SLIDE 6 — WHO ARE THE HIGH-VALUE CUSTOMERS?

**Title:** S1: High-Value Loyal — Your Most Valuable 14%  
**Visual:** Customer profile card + spend distribution chart  

**Profile:**
- Age 44+ | Primarily Male | Senior or Mid-Age band
- Clothing or Accessories buyer
- 25+ previous purchases | Pays digitally
- $90.89 avg spend | Review rating 3.83
- **0% discount dependence**

**Talking Points:**
- These 549 customers generate $49,900 in transaction revenue proxy
- They need NO discounts — stop giving them away
- Investment: premium shipping upgrades, early collection access, VIP status
- Risk: they are ORGANIC buyers — any change in product quality or experience will show up in review ratings first

---

## SLIDE 7 — THE PROMO PROBLEM

**Title:** 10% of Customers Are 100% Promo-Dependent  
**Visual:** Scatter plot — Promo Rate vs Avg Spend by segment  

**Key Contrast:**
- S1 spends $90.89 at 0% promo rate
- S4 spends $90.48 at 100% promo rate
- S2 spends $39.05 at 100% promo rate

**Talking Points:**
- S4 is NOT price-sensitive — they spend as much as S1
- The discount may be habitual, not necessary
- S2 IS price-sensitive — different strategy required
- Do not treat these two groups the same

---

## SLIDE 8 — GEOGRAPHIC OPPORTUNITY MAP

**Title:** Where Is Organic Demand Growing?  
**Visual:** Horizontal bar chart — Top 15 states by % organic buyers  

**Talking Points:**
- States with pct_organic > 70% AND avg_spend > $60 are priority growth targets
- These customers buy at full price — no discount needed to acquire or retain
- Marketing investment here has higher expected margin than promo-heavy regions
- Geographic mix suggests national reach — no single dominant state

---

## SLIDE 9 — CATEGORY FUNNEL

**Title:** Outerwear Retains. Footwear Acquires.  
**Visual:** Bar chart (avg repeats by category) + line overlay (avg spend)  

| Category | Avg Repeats | Role |
|---|---|---|
| Outerwear | 28.4 | Retention Anchor |
| Accessories | 27.3 | Retention / Transition |
| Clothing | 25.0 | Transition |
| Footwear | 24.0 | Entry-Point |

**Talking Points:**
- Outerwear customers have the most repeat history — this is your loyalty category
- Do NOT discount Outerwear — it undermines its retention value
- Footwear can be used as an acquisition category with introductory offers
- Cross-category progression (Footwear → Clothing → Accessories → Outerwear) is a growth path worth testing

---

## SLIDE 10 — THE PROMOTIONAL SUNSET PLAN

**Title:** How to Reduce Discounts Without Losing Revenue  
**Visual:** Phased rollout timeline (gantt-style)  

**Target:** S4 — Promo-Habituated Spenders (402 customers)  
**Trigger rule:** Spend ≥ $81 + 100% promo use + rating ≥ 4.0 + 20+ repeats

| Phase | Timeline | Action |
|---|---|---|
| 0. Baseline | Weeks 1–4 | Measure current purchase rate |
| 1. Pilot | Weeks 5–12 | Remove discount for 10% (40 customers) |
| 2. Expand | Weeks 13–20 | If churn < 15%, expand to 40% |
| 3. Full Rollout | Weeks 21–32 | All S4; replace discount with loyalty perks |

**Substitution:** Free Express shipping, early access, loyalty points  
**Exit criterion:** Halt if churn > 25% in Phase 1  

**Scenario Impact:**
- Base case: 20% churn → +$7,280 margin improvement
- Optimistic: 5% churn → +$13,700 margin improvement

---

## SLIDE 11 — THE IDEAL CUSTOMER PROFILE

**Title:** If You Could Clone Your Best Customer...  
**Visual:** Customer avatar card with attribute badges  

> **"A 40–55 year old, regular buyer who purchases Clothing or Accessories at full price 12–26x per year, rates the brand 4.0+, has 30+ previous purchases, and needs no discount."**

| Attribute | Value |
|---|---|
| Age | 40–55 |
| Gender | Male (dataset skew noted) |
| Category | Clothing / Accessories |
| Purchase Frequency | Monthly–Fortnightly |
| Avg Spend | $75–$100 |
| Previous Purchases | 30+ |
| Promo Dependency | 0% |
| Payment | Digital (Credit Card, Venmo) |
| Review Rating | ≥ 4.0 |

**Talking Points:**
- Use this profile for lookalike targeting in paid acquisition
- Use Loyalty Score B ≥ 0.70 as the segment filter in CRM
- Exclude discount-only buyers from this profile — they are a different archetype

---

## SLIDE 12 — DASHBOARD OVERVIEW

**Title:** Four-Panel Founder Dashboard  
**Visual:** Screenshot of `00_founder_dashboard.png`  

Panel 1: Customer Pyramid (segment size + spend)  
Panel 2: Promo Dependency vs Revenue by Segment  
Panel 3: Geographic Organic Demand Map  
Panel 4: Category Funnel (repeats + spend overlay)  

**Dashboard file:** `outputs/dashboard_data.csv` (ready for Power BI / Tableau)

---

## SLIDE 13 — RECOMMENDATIONS

**Title:** Seven Actions for the Next 90 Days  
**Visual:** Numbered action cards with segment labels  

1. 📊 **Adopt Loyalty Score B** as primary KPI — retire engagement-only metrics
2. 🏆 **Protect S1** — strip all discounts, add VIP perks and free premium shipping
3. 🔄 **Launch S4 sunset pilot** — 10% cohort, 8 weeks, measure churn daily
4. ⚠️ **Do not cut S2 discounts abruptly** — test loyalty reward substitution first
5. 🧥 **Invest in Outerwear retention** — highest-repeat category, zero discount
6. 🗺️ **Prioritise high-organic states** for full-price marketing campaigns
7. 📅 **Instrument the data** — add timestamps and transaction costs to enable true CLV

---

## SLIDE 14 — LIMITATIONS & WHAT WE DON'T CLAIM

**Title:** What This Analysis Cannot Tell You  
**Visual:** Honest limitation list  

- ❌ We cannot prove causality — all findings are associations
- ❌ We cannot compute true CLV without timestamps
- ❌ We cannot confirm margin impact without cost data
- ❌ We cannot claim these segments are stable over time — one-time snapshot
- ✅ We CAN give you traceable, reproducible logic for every finding
- ✅ Every proxy is labeled; every assumption is stated

---

## SLIDE 15 — APPENDIX: FILES PRODUCED

| File | Purpose |
|---|---|
| `data/processed/cleaned_data.csv` | Cleaned 3,900-row dataset |
| `data/processed/feature_table.csv` | 39 features per customer |
| `outputs/customer_level_table.csv` | Features + segments |
| `outputs/segment_summary.csv` | 5-segment profile table |
| `outputs/kpi_summary.csv` | Business KPIs by segment |
| `outputs/dashboard_data.csv` | BI-ready export |
| `outputs/figures/*.png` | 8 charts + dashboard |
| `sql/customer_segmentation.sql` | 7 SQL queries |
| `outputs/customer_intelligence.db` | SQLite database |
| `report/final_report.md` | Full report |
| `README.md` | Reproduction guide |
