-- Data Aggregation and Window Functions Example
-- Snowflake SQL

-- Example 1: Basic aggregation with time bucketing

WITH orders_grouped AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month
        , customer_id
        , COUNT(*) AS order_count
        , SUM(amount) AS total_amount
        , AVG(amount) AS avg_order_value
    FROM orders
    GROUP BY
        DATE_TRUNC('month', order_date)
        , customer_id
)

SELECT
    month
    , customer_id
    , order_count
    , total_amount
    , avg_order_value
WHERE
    AND total_amount > 1000
ORDER BY
    month DESC
    , total_amount DESC
LIMIT 500;


-- Example 2: Running totals and rankings

WITH customer_orders AS (
    SELECT
        customer_id
        , order_date
        , amount
        , SUM(amount) OVER (
            PARTITION BY customer_id 
            ORDER BY order_date
        ) AS running_total
        , RANK() OVER (
            PARTITION BY customer_id 
            ORDER BY amount DESC
        ) AS amount_rank
    FROM orders
)

SELECT
    customer_id
    , order_date
    , amount
    , running_total
    , amount_rank
WHERE
    AND amount_rank <= 3  -- Top 3 orders per customer
ORDER BY
    customer_id
    , order_date
LIMIT 100;


-- Example 3: Year-over-year comparison

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) AS month
        , YEAR(order_date) AS year
        , MONTH(order_date) AS month_num
        , SUM(amount) AS monthly_revenue
    FROM orders
    GROUP BY
        DATE_TRUNC('month', order_date)
        , YEAR(order_date)
        , MONTH(order_date)
)

SELECT
    month_num
    , MAX(CASE WHEN year = 2024 THEN monthly_revenue END) AS revenue_2024
    , MAX(CASE WHEN year = 2025 THEN monthly_revenue END) AS revenue_2025
    , COALESCE(
        (revenue_2025 - revenue_2024) / revenue_2024 * 100,
        0
    ) AS yoy_growth_pct
FROM monthly_sales
GROUP BY month_num
ORDER BY month_num
LIMIT 12;
