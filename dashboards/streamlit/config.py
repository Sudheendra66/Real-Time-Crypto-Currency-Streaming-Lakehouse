"""
Databricks connection configuration.
Uses environment variables to keep secrets out of the repository.
"""
import os
from dataclasses import dataclass


@dataclass
class DatabricksConfig:
    server_hostname: str = os.getenv("DATABRICKS_SERVER_HOSTNAME", "")
    http_path: str = os.getenv("DATABRICKS_HTTP_PATH", "")
    access_token: str = os.getenv("DATABRICKS_ACCESS_TOKEN", "")
    catalog: str = os.getenv("DATABRICKS_CATALOG", "hive_metastore")
    schema: str = os.getenv("DATABRICKS_SCHEMA", "default")


# Dashboard theme colors
class Theme:
    PRIMARY = "#6C63FF"        # Purple
    SECONDARY = "#00D4AA"      # Teal
    ACCENT = "#FF6B6B"         # Coral
    WARNING = "#FFD93D"        # Yellow
    DARK_BG = "#0E1117"        # Dark background
    CARD_BG = "#1A1D27"        # Card background
    TEXT_PRIMARY = "#FFFFFF"   # White text
    TEXT_SECONDARY = "#8892B0" # Muted text
    GRADIENT_START = "#6C63FF"
    GRADIENT_END = "#00D4AA"
    CHART_COLORS = [
        "#6C63FF", "#00D4AA", "#FF6B6B", "#FFD93D",
        "#4ECDC4", "#FF8C42", "#A78BFA", "#34D399",
        "#F472B6", "#60A5FA"
    ]