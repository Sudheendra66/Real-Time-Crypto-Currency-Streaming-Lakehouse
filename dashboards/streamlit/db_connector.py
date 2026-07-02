"""
Databricks SQL Warehouse connector using databricks-sql-connector.
Connects to DBT mart tables in Databricks.
"""
import pandas as pd
from databricks import sql
from config import DatabricksConfig


def get_connection():
    """Create and return a Databricks SQL connection."""
    config = DatabricksConfig()
    conn = sql.connect(
        server_hostname=config.server_hostname,
        http_path=config.http_path,
        access_token=config.access_token,
        catalog=config.catalog,
        schema=config.schema,
    )
    return conn


def query_to_df(query: str) -> pd.DataFrame:
    """Execute a SQL query and return results as a pandas DataFrame."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            data = [list(row) for row in rows]
            df = pd.DataFrame(data, columns=columns)
        return df
    finally:
        conn.close()


# ─── Pre-built queries for each mart ────────────────────────────────────────

QUERY_MARKET_OVERVIEW = """
SELECT * FROM hive_metastore.default.market_overview
"""

QUERY_CRYPTO_SUMMARY = """
SELECT * FROM hive_metastore.default.crypto_summary
ORDER BY total_volume DESC
"""

QUERY_TOP_VOLUME = """
SELECT * FROM hive_metastore.default.top_volume_assets
"""

# asset_performance doesn't exist as a table, so we compute it from crypto_summary
QUERY_ASSET_PERFORMANCE = """
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
FROM hive_metastore.default.crypto_summary
ORDER BY total_volume DESC
"""


def get_market_overview() -> pd.DataFrame:
    return query_to_df(QUERY_MARKET_OVERVIEW)


def get_crypto_summary() -> pd.DataFrame:
    return query_to_df(QUERY_CRYPTO_SUMMARY)


def get_top_volume() -> pd.DataFrame:
    return query_to_df(QUERY_TOP_VOLUME)


def get_asset_performance() -> pd.DataFrame:
    return query_to_df(QUERY_ASSET_PERFORMANCE)