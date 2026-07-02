{{ config(materialized='table') }}

SELECT
    symbol,
    avg_price,
    max_price,
    min_price,
    (max_price - min_price) / NULLIF(min_price, 0) * 100 AS price_volatility_pct,
    total_volume,
    total_trade_value,
    number_of_trades,
    total_trade_value / NULLIF(total_volume, 0) AS avg_trade_value_per_unit,
    total_volume / NULLIF(number_of_trades, 0) AS avg_volume_per_trade
FROM {{ ref('stg_gold_crypto') }}