{{ config(materialized='table') }}

SELECT
    symbol,
    total_volume,
    total_trade_value,
    number_of_trades
FROM {{ ref('stg_gold_crypto') }}
ORDER BY total_volume DESC