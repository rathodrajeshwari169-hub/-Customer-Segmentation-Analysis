-- customer_segmentation.sql
-- D2C Fashion Customer Intelligence — Analytical SQL
-- Compatible with SQLite. All queries use CTEs or simple SELECT.
-- Run against the customer_level_table loaded into 'customers' table.

-- TABLE CREATION (run once):
-- CREATE TABLE customers AS SELECT * FROM read_csv('outputs/customer_level_table.csv');


-- =======================================================
-- Q1_HIGH_VALUE_PROFILES
-- =======================================================

-- Q1: Which customer profiles are genuinely high value?
-- High value = top 25% spend, high commercial loyalty (tier B = High), no promo dependency
SELECT
    age_band,
    gender,
    category,
    season,
    location,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 2) AS avg_repeat,
    ROUND(AVG(loyalty_score_B), 3) AS avg_loyalty_B,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(100.0 * SUM(promo_flag) / COUNT(*), 1) AS pct_promo
FROM customers
WHERE high_value_flag = 1 AND loyalty_tier_B = 'High'
GROUP BY age_band, gender, category, season, location
HAVING customer_count >= 3
ORDER BY avg_spend DESC, avg_loyalty_B DESC
LIMIT 30;


-- =======================================================
-- Q2_PROMO_DEPENDENT
-- =======================================================

-- Q2: Which customers appear promo-dependent?
-- Promo-dependent = both discount AND promo code used, spend below median (60 USD)
SELECT
    segment_label,
    age_band,
    gender,
    category,
    location,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(AVG(promo_dependency_score), 3) AS avg_promo_score,
    ROUND(AVG(previous_purchases), 2) AS avg_repeats,
    ROUND(AVG(review_rating), 2) AS avg_rating
FROM customers
WHERE promo_flag = 1
GROUP BY segment_label, age_band, gender, category, location
ORDER BY avg_promo_score DESC, customer_count DESC
LIMIT 30;


-- =======================================================
-- Q3_GEOGRAPHIC_OPPORTUNITY
-- =======================================================

-- Q3: Which geographies show organic demand (high spend WITHOUT promo dependency)?
SELECT
    location,
    COUNT(*) AS total_customers,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(100.0 * SUM(CASE WHEN promo_flag = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_organic,
    ROUND(AVG(CASE WHEN promo_flag = 0 THEN purchase_amount END), 2) AS organic_avg_spend,
    ROUND(AVG(loyalty_score_B), 3) AS avg_loyalty_B,
    ROUND(AVG(previous_purchases), 2) AS avg_repeats
FROM customers
GROUP BY location
HAVING total_customers >= 20
ORDER BY pct_organic DESC, organic_avg_spend DESC
LIMIT 30;


-- =======================================================
-- Q4_CATEGORY_SEASON_FUNNEL
-- =======================================================

-- Q4: Entry-point vs retention categories and seasons
-- Entry: lower previous_purchases (new buyers), Retention: higher previous_purchases
SELECT
    season,
    category,
    COUNT(*) AS customer_count,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 2) AS avg_repeats,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(100.0 * SUM(promo_flag) / COUNT(*), 1) AS pct_promo,
    ROUND(100.0 * SUM(subscription_status) / COUNT(*), 1) AS pct_subscribed,
    ROUND(AVG(loyalty_score_B), 3) AS avg_loyalty_B
FROM customers
GROUP BY season, category
ORDER BY avg_repeats DESC;


-- =======================================================
-- Q5_IDEAL_CUSTOMER_PROFILE
-- =======================================================

-- Q5: What does the ideal customer profile look like?
-- Ideal = top 20% spend, no promo dependency, high satisfaction, high repeats
WITH ideal AS (
    SELECT * FROM customers
    WHERE loyalty_tier_B = 'High'
      AND promo_flag = 0
      AND satisfaction_flag = 1
      AND previous_purchases >= 25
)
SELECT
    'IDEAL CUSTOMER PROFILE' AS profile,
    COUNT(*) AS count,
    ROUND(AVG(age), 1) AS avg_age,
    (SELECT gender FROM ideal GROUP BY gender ORDER BY COUNT(*) DESC LIMIT 1) AS modal_gender,
    (SELECT age_band FROM ideal GROUP BY age_band ORDER BY COUNT(*) DESC LIMIT 1) AS modal_age_band,
    (SELECT category FROM ideal GROUP BY category ORDER BY COUNT(*) DESC LIMIT 1) AS top_category,
    (SELECT season FROM ideal GROUP BY season ORDER BY COUNT(*) DESC LIMIT 1) AS top_season,
    (SELECT location FROM ideal GROUP BY location ORDER BY COUNT(*) DESC LIMIT 1) AS top_location,
    (SELECT payment_method FROM ideal GROUP BY payment_method ORDER BY COUNT(*) DESC LIMIT 1) AS top_payment,
    (SELECT shipping_type FROM ideal GROUP BY shipping_type ORDER BY COUNT(*) DESC LIMIT 1) AS top_shipping,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(AVG(previous_purchases), 2) AS avg_repeats,
    ROUND(AVG(purchases_per_year), 1) AS avg_freq_per_year,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(AVG(loyalty_score_B), 3) AS avg_loyalty_B
FROM ideal;


-- =======================================================
-- Q6_PROMO_SUNSET_CANDIDATES
-- =======================================================

-- Q6: Promo Sunset Candidates — high spenders who use promos but could sustain without
-- These are Promo-Habituated Spenders (S4) with high review ratings
SELECT
    customer_id,
    age,
    gender,
    age_band,
    category,
    location,
    purchase_amount,
    previous_purchases,
    review_rating,
    loyalty_score_B,
    promo_dependency_score,
    segment_label,
    purchases_per_year,
    spend_x_frequency
FROM customers
WHERE segment_code = 'S4'
  AND review_rating >= 4.0
ORDER BY purchase_amount DESC, loyalty_score_B DESC
LIMIT 50;


-- =======================================================
-- Q7_KPI_SUMMARY
-- =======================================================

-- Q7: Overall KPI summary by segment
SELECT
    segment_code,
    segment_label,
    COUNT(*) AS n_customers,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM customers), 1) AS pct_total,
    ROUND(AVG(purchase_amount), 2) AS avg_spend,
    ROUND(SUM(purchase_amount), 2) AS total_revenue_proxy,
    ROUND(AVG(previous_purchases), 2) AS avg_repeats,
    ROUND(AVG(review_rating), 2) AS avg_rating,
    ROUND(100.0 * AVG(promo_flag), 1) AS promo_rate_pct,
    ROUND(100.0 * AVG(subscription_status), 1) AS subscription_rate_pct,
    ROUND(AVG(loyalty_score_A), 3) AS avg_loyalty_A,
    ROUND(AVG(loyalty_score_B), 3) AS avg_loyalty_B,
    ROUND(AVG(spend_x_frequency), 1) AS avg_annualised_value
FROM customers
GROUP BY segment_code, segment_label
ORDER BY avg_spend DESC;
