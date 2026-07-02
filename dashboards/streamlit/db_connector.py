"""
Databricks SQL Warehouse connector using databricks-sql-connector.
Connects to DBT mart tables in Databricks.
"""
import pandas as pd
from databricks import sql
from config import DatabricksConfig


def get_config():
    """Load and return the Databricks configuration from Streamlit secrets."""
    return DatabricksConfig.from_secrets()


def get_connection():
    """Create and return a Databricks SQL connection."""
    config = get_config()
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


def _full_table_name(config: DatabricksConfig, table: str) -> str:
    """Return a fully-qualified table name using catalog and schema from config."""
    return f"{config.catalog}.{config.schema}.{table}"


def _build_query_market_overview(config: DatabricksConfig) -> str:
    tbl = _full_table_name(config, "market_overview")
    return f"SELECT * FROM {tbl}"


def _build_query_crypto_summary(config: DatabricksConfig) -> str:
    tbl = _full_table_name(config, "crypto_summary")
    return f"SELECT * FROM {tbl} ORDER BY total_volume DESC"


def _build_query_top_volume(config: DatabricksConfig) -> str:
    tbl = _full_table_name(config, "top_volume_assets")
    return f"SELECT * FROM {tbl}"


def _build_query_asset_performance(config: DatabricksConfig) -> str:
    tbl = _full_table_name(config, "crypto_summary")
    return f"""
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
FROM {tbl}
ORDER BY total_volume DESC
"""


def get_market_overview() -> pd.DataFrame:
    config = get_config()
    return query_to_df(_build_query_market_overview(config))


def get_crypto_summary() -> pd.DataFrame:
    config = get_config()
    return query_to_df(_build_query_crypto_summary(config))


def get_top_volume() -> pd.DataFrame:
    config = get_config()
    return query_to_df(_build_query_top_volume(config))


def get_asset_performance() -> pd.DataFrame:
    config = get_config()
    return query_to_df(_build_query_asset_performance(config))
