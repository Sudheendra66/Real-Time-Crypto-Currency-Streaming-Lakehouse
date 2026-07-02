-- Assert that avg_price is always positive (> 0) in stg_gold_crypto
SELECT
    symbol,
    avg_price
FROM {{ ref('stg_gold_crypto') }}
WHERE avg_price <= 0