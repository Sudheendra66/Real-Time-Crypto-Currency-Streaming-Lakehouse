-- Assert that symbol is never null in stg_gold_crypto
SELECT
    symbol
FROM {{ ref('stg_gold_crypto') }}
WHERE symbol IS NULL