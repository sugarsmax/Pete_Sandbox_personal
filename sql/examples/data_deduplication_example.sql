-- Data Deduplication Example
-- Common pattern: Keep first occurrence, mark/remove duplicates
-- Snowflake SQL

-- Example 1: Identify duplicates using ROW_NUMBER()

WITH base_data AS (
    SELECT
        customer_id
        , order_date
        , amount
        , ROW_NUMBER() OVER (PARTITION BY customer_id, order_date ORDER BY created_at) AS rn
    FROM orders
)

SELECT
    customer_id
    , order_date
    , amount
WHERE
    AND rn = 1  -- Keep only first occurrence
LIMIT 100;


-- Example 2: Find and count duplicate groups

WITH duplicate_analysis AS (
    SELECT
        customer_id
        , order_date
        , COUNT(*) AS duplicate_count
    FROM orders
    GROUP BY
        customer_id
        , order_date
)

SELECT
    customer_id
    , order_date
    , duplicate_count
WHERE
    AND duplicate_count > 1
ORDER BY duplicate_count DESC
LIMIT 50;


-- Example 3: Mark duplicates with flag for review

WITH ranked_data AS (
    SELECT
        *
        , ROW_NUMBER() OVER (PARTITION BY customer_id, order_date ORDER BY created_at) AS row_num
    FROM orders
)

SELECT
    *
    , CASE WHEN row_num = 1 THEN FALSE ELSE TRUE END AS is_duplicate
FROM ranked_data
WHERE
    AND is_duplicate = TRUE
LIMIT 1000;
