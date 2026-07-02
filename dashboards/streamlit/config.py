"""
Databricks connection configuration.
Uses Streamlit secrets to keep credentials out of the repository.
"""
import streamlit as st
from dataclasses import dataclass


@dataclass
class DatabricksConfig:
    server_hostname: str = ""
    http_path: str = ""
    access_token: str = ""
    catalog: str = "hive_metastore"
    schema: str = "default"

    @classmethod
    def from_secrets(cls) -> "DatabricksConfig":
        """Load Databricks configuration from Streamlit secrets."""
        try:
            dbx = st.secrets["databricks"]
            return cls(
                server_hostname=dbx.get("server_hostname", ""),
                http_path=dbx.get("http_path", ""),
                access_token=dbx.get("access_token", ""),
                catalog=dbx.get("catalog", "hive_metastore"),
                schema=dbx.get("schema", "default"),
            )
        except KeyError:
            raise ValueError(
                "Missing 'databricks' section in secrets. "
                "Please configure your Databricks connection in "
                ".streamlit/secrets.toml or Streamlit Cloud secrets."
            )


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