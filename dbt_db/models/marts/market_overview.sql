{{ config(materialized='table') }}

SELECT
    COUNT(DISTINCT symbol) AS total_assets,
    SUM(total_trade_value) AS total_market_value,
    SUM(number_of_trades) AS total_trades,
    AVG(avg_price) AS average_asset_price
FROM {{ ref('stg_gold_crypto') }}