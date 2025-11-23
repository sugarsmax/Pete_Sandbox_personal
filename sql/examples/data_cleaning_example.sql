-- Data Cleaning Example
-- Common patterns: type conversions, null handling, standardization
-- Snowflake SQL

-- Example 1: Standardize and clean user data

WITH raw_users AS (
    SELECT
        user_id
        , TRIM(UPPER(name)) AS name
        , LOWER(TRIM(email)) AS email
        , CASE 
            WHEN phone_number IS NULL THEN NULL
            WHEN REGEXP_SUBSTR(phone_number, '[0-9]') IS NULL THEN NULL
            ELSE REGEXP_REPLACE(phone_number, '[^0-9]', '')
        END AS phone_clean
        , COALESCE(age, 0) AS age
        , CASE 
            WHEN LOWER(status) IN ('active', 'enabled') THEN 'active'
            WHEN LOWER(status) IN ('inactive', 'disabled') THEN 'inactive'
            ELSE 'unknown'
        END AS status_normalized
    FROM raw_user_table
)

SELECT
    user_id
    , name
    , email
    , phone_clean
    , age
    , status_normalized
WHERE
    AND email NOT LIKE '%@%.%'  -- Filter invalid emails
    AND age >= 0 AND age <= 150  -- Reasonable age range
LIMIT 1000;


-- Example 2: Handle NULL values strategically

WITH transaction_data AS (
    SELECT
        transaction_id
        , customer_id
        , transaction_date
        , amount
        , description
        , COALESCE(category, 'Uncategorized') AS category
        , COALESCE(
            notes,
            'No notes provided'
        ) AS notes_filled
        , CASE 
            WHEN refund_amount IS NULL THEN 0 
            ELSE refund_amount 
        END AS refund_amount
        , CASE 
            WHEN transaction_date IS NULL 
                THEN CURRENT_DATE 
            ELSE transaction_date 
        END AS date_filled
    FROM raw_transactions
)

SELECT
    transaction_id
    , customer_id
    , date_filled
    , amount
    , refund_amount
    , category
WHERE
    AND refund_amount > 0  -- Only refunded transactions
LIMIT 500;


-- Example 3: Detect and flag data quality issues

WITH quality_check AS (
    SELECT
        product_id
        , product_name
        , price
        , CASE 
            WHEN product_name IS NULL 
                THEN 'missing_name' 
            WHEN LENGTH(TRIM(product_name)) = 0 
                THEN 'empty_name'
            ELSE NULL 
        END AS name_issue
        , CASE 
            WHEN price IS NULL 
                THEN 'missing_price'
            WHEN price < 0 
                THEN 'negative_price'
            WHEN price > 999999 
                THEN 'suspicious_price'
            ELSE NULL 
        END AS price_issue
        , CASE 
            WHEN created_date IS NULL 
                OR created_date > CURRENT_TIMESTAMP() 
                THEN 'date_issue'
            ELSE NULL 
        END AS date_issue
    FROM products
)

SELECT
    product_id
    , product_name
    , price
    , CONCAT_WS(
        ', ',
        NULLIF(name_issue, NULL),
        NULLIF(price_issue, NULL),
        NULLIF(date_issue, NULL)
    ) AS quality_issues
WHERE
    AND quality_issues IS NOT NULL
LIMIT 100;
