"""
Streamlit Dashboard: DBT Marts Insights Dashboard
Connects to Databricks SQL Warehouse and visualizes DBT model outputs.
"""
import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import Theme, DatabricksConfig

# ─── Page config (MUST be the first Streamlit command) ──────────────────────
st.set_page_config(
    page_title="Crypto & Gold Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Beginner-friendly coin information ─────────────────────────────────────
# Maps raw ticker symbols to plain-language names, icons, and descriptions
COIN_INFO = {
    "BTC":  {"name": "Bitcoin",       "icon": "🟡", "description": "The original cryptocurrency — like digital gold."},
    "ETH":  {"name": "Ethereum",      "icon": "💎", "description": "A platform for apps and smart contracts."},
    "SOL":  {"name": "Solana",        "icon": "🌞", "description": "A fast blockchain for decentralized apps."},
    "XRP":  {"name": "XRP",           "icon": "💠", "description": "A digital payment network for fast transfers."},
    "BNB":  {"name": "BNB",           "icon": "🟡", "description": "The native token of the Binance exchange."},
    "ADA":  {"name": "Cardano",       "icon": "🟢", "description": "A blockchain focused on security and sustainability."},
    "DOT":  {"name": "Polkadot",      "icon": "🟣", "description": "Connects different blockchains together."},
    "AVAX": {"name": "Avalanche",     "icon": "🔴", "description": "A fast platform for decentralized apps."},
    "LINK": {"name": "Chainlink",     "icon": "🔗", "description": "Brings real-world data onto blockchains."},
    "MATIC":{"name": "Polygon",       "icon": "🟪", "description": "Makes Ethereum faster and cheaper to use."},
    "ATOM": {"name": "Cosmos",        "icon": "☄️", "description": "Helps different blockchains talk to each other."},
    "UNI":  {"name": "Uniswap",       "icon": "🦄", "description": "A popular app for swapping cryptocurrencies."},
    "AAVE": {"name": "Aave",          "icon": "💜", "description": "A platform for lending and borrowing crypto."},
}

# Mapping from full ticker symbols (e.g., "BTCUSDT") to display names
TICKER_DISPLAY_MAP = {
    "BTCUSDT": "Bitcoin (BTC)",
    "ETHUSDT": "Ethereum (ETH)",
    "BNBUSDT": "BNB (BNB)",
    "SOLUSDT": "Solana (SOL)",
    "XRPUSDT": "XRP (XRP)",
}


def get_display_label(symbol):
    """Return a beginner-friendly label like 'Bitcoin (BTC)' with icon."""
    # First check the explicit ticker mapping
    if symbol in TICKER_DISPLAY_MAP:
        display_name = TICKER_DISPLAY_MAP[symbol]
        # Extract the short symbol (e.g., "BTC" from "Bitcoin (BTC)")
        short_symbol = symbol.replace("USDT", "")
        info = COIN_INFO.get(short_symbol, {})
        icon = info.get("icon", "🪙")
        return f"{icon} {display_name}"

    # Fallback: strip "USDT" and capitalize
    short_symbol = symbol.replace("USDT", "")
    info = COIN_INFO.get(short_symbol, {})
    name = info.get("name", short_symbol)
    icon = info.get("icon", "🪙")
    return f"{icon} {name} ({short_symbol})"


def get_short_label(symbol):
    """Return a short label like 'Bitcoin (BTC)' without icon."""
    # First check the explicit ticker mapping
    if symbol in TICKER_DISPLAY_MAP:
        return TICKER_DISPLAY_MAP[symbol]

    # Fallback: strip "USDT" and capitalize
    short_symbol = symbol.replace("USDT", "")
    info = COIN_INFO.get(short_symbol, {})
    name = info.get("name", short_symbol)
    return f"{name} ({short_symbol})"


def get_coin_description(symbol):
    """Return a one-line description of the coin."""
    # Extract short symbol from full ticker
    short_symbol = symbol.replace("USDT", "")
    info = COIN_INFO.get(short_symbol, {})
    return info.get("description", "")


# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    /* ── Base ── */
    .stApp {{
        background-color: {Theme.DARK_BG};
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        background: linear-gradient(180deg, {Theme.DARK_BG} 0%, {Theme.CARD_BG} 100%);
        border-right: 1px solid rgba(108,99,255,0.2);
    }}
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label {{
        color: {Theme.TEXT_SECONDARY} !important;
    }}

    /* ── Sidebar Navigation Selectbox ── */
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {{
        margin-bottom: 8px;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div {{
        background: rgba(108,99,255,0.15) !important;
        border: 1px solid rgba(108,99,255,0.4) !important;
        border-radius: 12px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div:hover {{
        border-color: rgba(108,99,255,0.7) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
    }}

    /* ── Metric Cards ── */
    div[data-testid="metric-container"] {{
        background: linear-gradient(135deg, #1F2240 0%, #25284D 100%) !important;
        border: 1px solid rgba(108,99,255,0.35) !important;
        border-radius: 16px !important;
        padding: 20px 16px 12px 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    div[data-testid="metric-container"]::before {{
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, {Theme.PRIMARY}, {Theme.SECONDARY});
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(108,99,255,0.35) !important;
        border-color: rgba(108,99,255,0.55) !important;
    }}
    /* Metric label */
    div[data-testid="metric-container"] label {{
        color: #B0B8D0 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }}
    /* Metric value - force white */
    div[data-testid="metric-container"] [data-testid="stMetricValue"],
    div[data-testid="metric-container"] div:last-child {{
        color: #FFFFFF !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        text-shadow: 0 0 25px rgba(108,99,255,0.3) !important;
    }}

    /* ── Typography ── */
    h1, h2, h3 {{
        color: {Theme.TEXT_PRIMARY} !important;
        font-weight: 600 !important;
    }}

    /* ── Cards ── */
    .insight-card {{
        background: {Theme.CARD_BG};
        border: 1px solid rgba(108,99,255,0.15);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }}
    .insight-card:hover {{
        border-color: rgba(108,99,255,0.3);
        box-shadow: 0 6px 25px rgba(0,0,0,0.4);
    }}
    .insight-card h4 {{
        color: {Theme.PRIMARY};
        margin-bottom: 12px;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .insight-card p {{
        color: {Theme.TEXT_SECONDARY};
        line-height: 1.7;
    }}
    .insight-card .highlight {{
        color: {Theme.SECONDARY};
        font-weight: 600;
    }}

    /* ── Dataframe ── */
    .stDataFrame {{
        background: {Theme.CARD_BG};
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(108,99,255,0.1);
    }}
    .stDataFrame th {{
        background: rgba(108,99,255,0.15) !important;
        color: {Theme.PRIMARY} !important;
        font-weight: 600 !important;
    }}
    .stDataFrame td {{
        background: {Theme.CARD_BG} !important;
        color: {Theme.TEXT_PRIMARY} !important;
    }}

    /* ── Podium cards ── */
    .podium-card {{
        text-align: center;
        background: {Theme.CARD_BG};
        border: 1px solid rgba(108,99,255,0.15);
        border-radius: 20px;
        padding: 28px 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .podium-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }}
    .podium-card .medal {{
        font-size: 3rem;
        margin-bottom: 8px;
    }}
    .podium-card .symbol {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 8px 0;
        color: {Theme.TEXT_PRIMARY};
    }}
    .podium-card .stat-box {{
        background: rgba(108,99,255,0.1);
        border-radius: 12px;
        padding: 12px;
        margin: 12px 0;
    }}
    .podium-card .stat-label {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }}
    .podium-card .stat-value {{
        font-size: 1.4rem;
        font-weight: 700;
        margin: 4px 0 0 0;
    }}
    .podium-card .stat-row {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.85rem;
        margin: 4px 0;
    }}
    .podium-card .stat-row span {{
        font-weight: 600;
    }}

    /* ── Source badge ── */
    .source-badge {{
        padding: 10px 16px;
        background: rgba(108,99,255,0.08);
        border-radius: 10px;
        margin-bottom: 16px;
        border: 1px solid rgba(108,99,255,0.1);
    }}
    .source-badge .label {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.75rem;
        margin: 0 0 2px 0;
    }}
    .source-badge .value {{
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0;
    }}

    /* ── Nav section ── */
    .nav-section {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        font-weight: 500;
    }}

    /* ── Filter section ── */
    .filter-section {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
        font-weight: 500;
    }}
    hr.divider {{
        border-color: rgba(108,99,255,0.1);
        margin: 20px 0;
    }}

    /* ── Footer ── */
    .footer {{
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        border-top: 1px solid rgba(108,99,255,0.1);
    }}
    .footer p {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.8rem;
        margin: 0;
    }}

    /* ── DBT models box ── */
    .dbt-models-box {{
        margin-top: 20px;
        padding: 16px;
        background: linear-gradient(135deg, rgba(108,99,255,0.1), rgba(0,212,170,0.1));
        border-radius: 12px;
        border: 1px solid rgba(108,99,255,0.15);
    }}
    .dbt-models-box .label {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.7rem;
        margin: 0 0 4px 0;
    }}
    .dbt-models-box .models {{
        color: {Theme.TEXT_PRIMARY};
        font-size: 0.8rem;
        margin: 0;
    }}

    /* ── Explainer banner ── */
    .explainer-banner {{
        background: linear-gradient(135deg, rgba(108,99,255,0.12), rgba(0,212,170,0.08));
        border: 1px solid rgba(108,99,255,0.2);
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .explainer-banner .icon {{
        font-size: 1.5rem;
    }}
    .explainer-banner .text {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.95rem;
        margin: 0;
        line-height: 1.5;
    }}
    .explainer-banner .text strong {{
        color: {Theme.TEXT_PRIMARY};
    }}

    /* ── Y-axis subtitle ── */
    .yaxis-subtitle {{
        color: {Theme.TEXT_SECONDARY};
        font-size: 0.75rem;
        font-style: italic;
        margin-top: -8px;
        margin-bottom: 8px;
    }}
</style>
""", unsafe_allow_html=True)

# ─── Data Loading ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_data():
    """
    Load data from Databricks SQL Warehouse.
    """
    from db_connector import (
        get_market_overview,
        get_crypto_summary,
        get_top_volume,
        get_asset_performance,
    )
    df_overview = get_market_overview()
    df_summary = get_crypto_summary()
    df_top = get_top_volume()
    df_perf = get_asset_performance()
    return df_overview, df_summary, df_top, df_perf


try:
    # Validate secrets are configured before attempting connection
    DatabricksConfig.from_secrets()
    df_overview, df_summary, df_top, df_perf = load_data()
    data_source = "Databricks SQL Warehouse"
    connection_ok = True
except ValueError as ve:
    st.error("🔐 **Missing Databricks Configuration**")
    st.error(f"`{ve}`")
    st.info(
        "To configure, create a `.streamlit/secrets.toml` file in the project root "
        "with your Databricks connection details, or configure secrets in "
        "Streamlit Cloud dashboard."
    )
    st.markdown(
        "**Required secrets format:**\n\n"
        "```toml\n"
        "[databricks]\n"
        "server_hostname = \"your-workspace.azuredatabricks.net\"\n"
        "http_path = \"/sql/1.0/warehouses/your-warehouse-id\"\n"
        "access_token = \"dapi-your-token\"\n"
        "catalog = \"hive_metastore\"\n"
        "schema = \"default\"\n"
        "```"
    )
    st.stop()
except Exception as e:
    st.error("❌ **Databricks connection failed** — unable to load dashboard data.")
    st.error(f"Error: `{e}`")
    st.info(
        "Please verify:\n"
        "1. Your Databricks SQL Warehouse is running\n"
        "2. The required tables exist (market_overview, crypto_summary, top_volume_assets)\n"
        "3. Your credentials in secrets are correct"
    )
    st.stop()


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:20px 10px; border-bottom:1px solid rgba(108,99,255,0.2); margin-bottom:20px;">
        <div style="font-size:2.5rem; margin-bottom:8px; background:linear-gradient(135deg, {Theme.PRIMARY}, {Theme.SECONDARY}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">📊</div>
        <h3 style="color:white; margin:0; font-weight:700;">Market Intelligence</h3>
        <p style="color:{Theme.TEXT_SECONDARY}; font-size:0.8rem; margin:4px 0 0 0;">
            Powered by DBT & Databricks
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="source-badge">
        <p class="label">LIVE CRYPTO CURRENCY DASHBOARD</p>
        <p class="value" style="color: #00E676;">🟢 Live · {data_source}</p>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<p class="nav-section">Navigation</p>', unsafe_allow_html=True)
    page = st.selectbox(
        "Navigation",
        ["🏠 Market Overview", "📈 Asset Analysis", "🏆 Volume Leaders", "⚡ Performance"],
        label_visibility="collapsed",
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Global filters
    st.markdown('<p class="filter-section">Filters</p>', unsafe_allow_html=True)

    all_symbols = sorted(df_summary["symbol"].tolist())
    # Use display labels in the multiselect (show short names only, not full ticker)
    symbol_display_map = {s: get_short_label(s) for s in all_symbols}
    selected_displays = st.multiselect(
        "Select Assets",
        options=[symbol_display_map[s] for s in all_symbols],
        default=[symbol_display_map[s] for s in all_symbols[:6]] if len(all_symbols) > 6 else [symbol_display_map[s] for s in all_symbols],
        label_visibility="collapsed",
    )
    # Map display labels back to raw symbols
    reverse_map = {v: k for k, v in symbol_display_map.items()}
    selected_symbols = [reverse_map[d] for d in selected_displays] if selected_displays else all_symbols

    min_volume, max_volume = int(df_summary["total_volume"].min()), int(df_summary["total_volume"].max())
    if min_volume < max_volume:
        volume_range = st.slider(
            "Volume Range",
            min_value=min_volume,
            max_value=max_volume,
            value=(min_volume, max_volume),
            label_visibility="collapsed",
        )
    else:
        volume_range = (min_volume, max_volume)

    st.markdown(f"""
    <div class="dbt-models-box">
        <p class="label">DBT MODELS</p>
        <p class="models">
            • market_overview<br>
            • crypto_summary<br>
            • top_volume_assets<br>
            • asset_performance
        </p>
    </div>
    """, unsafe_allow_html=True)

# Filter data based on sidebar selections
df_summary_f = df_summary[
    (df_summary["symbol"].isin(selected_symbols)) &
    (df_summary["total_volume"].between(volume_range[0], volume_range[1])
)]
df_perf_f = df_perf[
    df_perf["symbol"].isin(selected_symbols)
]
df_top_f = df_top[
    df_top["symbol"].isin(selected_symbols)
]


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def format_currency(value):
    """Format large numbers into human-readable currency strings."""
    if abs(value) >= 1_000_000_000:
        return f"${value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"${value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.2f}K"
    return f"${value:.2f}"


def format_number(value):
    """Format large numbers into human-readable strings."""
    if abs(value) >= 1_000_000_000:
        return f"{value/1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{value/1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{value/1_000:.2f}K"
    return f"{value:.2f}"


def create_chart_colorscale(colors_list):
    """Create a continuous colorscale from theme colors."""
    n = len(colors_list)
    return [(i / (n - 1), c) for i, c in enumerate(colors_list)]


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1: MARKET OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════

if "Overview" in page:

    # ── Header ──
    st.markdown("""
    <div style="display:flex; align-items:center; gap:16px; margin-bottom:4px;">
        <h1 style="font-size:2.2rem; margin:0;">🏠 Market Overview</h1>
    </div>
    """, unsafe_allow_html=True)

    # ── Beginner-friendly explainer banner ──
    st.markdown("""
    <div class="explainer-banner">
        <div class="icon">ℹ️</div>
        <p class="text">
            <strong>Track how popular cryptocurrencies are performing right now</strong> — no experience needed.
            Each coin has an icon and a plain-language name so you can recognize them at a glance.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='color:{Theme.TEXT_SECONDARY}; font-size:1rem; margin-top:0;'>Key metrics and insights from your DBT <code>market_overview</code> mart</p>", unsafe_allow_html=True)

    ov = df_overview.iloc[0]

    # ── Key Metrics Row ──
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Assets", ov["total_assets"], delta=None)
    with col2:
        st.metric("Total Market Value", format_currency(ov["total_market_value"]))
    with col3:
        st.metric("Total Trades", format_number(ov["total_trades"]))
    with col4:
        st.metric("Average Price", f"${ov['average_asset_price']:.2f}")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Row 2: Charts ──
    col1, col2 = st.columns([0.55, 0.45])

    with col1:
        st.markdown(f"<div class='insight-card'><h4>📊 Portfolio Distribution — Trade Value</h4>", unsafe_allow_html=True)
        # Use display labels in pie chart
        df_pie = df_summary_f.copy()
        df_pie["display_label"] = df_pie["symbol"].apply(get_short_label)
        fig_pie = px.pie(
            df_pie,
            values="total_trade_value",
            names="display_label",
            color_discrete_sequence=Theme.CHART_COLORS,
            hole=0.5,
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color=Theme.TEXT_SECONDARY), orientation="h", y=-0.15),
            margin=dict(l=10, r=10, t=10, b=10),
            height=420,
        )
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(color="white", size=11),
            marker=dict(line=dict(color=Theme.DARK_BG, width=2)),
            hovertemplate="<b>%{label}</b><br>Value: %{value:$,.0f}<br>Share: %{percent}<extra></extra>",
        )
        st.plotly_chart(fig_pie, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

        # — Insight in plain language —
        if not df_summary_f.empty:
            top_asset = df_summary_f.sort_values("total_trade_value", ascending=False).iloc[0]
            top_pct = top_asset["total_trade_value"] / ov["total_market_value"] * 100 if ov["total_market_value"] > 0 else 0
            top_label = get_short_label(top_asset["symbol"])
            st.markdown(f"""
            <div class='insight-card'>
                <h4>💡 Key Insight</h4>
                <p>
                    <span class='highlight'>{top_label}</span> is the most traded cryptocurrency right now,
                    with <span class='highlight'>{format_currency(top_asset['total_trade_value'])}</span> worth of trades.
                    That's <span class='highlight'>{top_pct:.1f}%</span> of the entire market value of
                    <span class='highlight'>{format_currency(ov['total_market_value'])}</span> —
                    similar to one company making up most of a stock market index.
                </p>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='insight-card'><h4>📈 Volume vs Trade Value</h4>", unsafe_allow_html=True)
        df_scatter = df_perf_f.copy()
        df_scatter["display_label"] = df_scatter["symbol"].apply(get_short_label)
        fig_scatter = px.scatter(
            df_scatter,
            x="total_volume",
            y="total_trade_value",
            size="avg_price",
            color="display_label",
            color_discrete_sequence=Theme.CHART_COLORS,
            text="display_label",
            log_x=True,
            log_y=True,
            hover_data={
                "total_volume": ":,.0f",
                "total_trade_value": ":$,.0f",
                "avg_price": "$,.2f",
                "display_label": False,
            },
        )
        fig_scatter.update_traces(
            textposition="top center",
            marker=dict(line=dict(width=1, color=Theme.DARK_BG), opacity=0.85),
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Total Volume (log scale)", color=Theme.TEXT_SECONDARY,
                gridcolor="rgba(255,255,255,0.05)", title_font=dict(size=12),
            ),
            yaxis=dict(
                title="Trade Value (log scale)", color=Theme.TEXT_SECONDARY,
                gridcolor="rgba(255,255,255,0.05)", title_font=dict(size=12),
            ),
            legend=dict(font=dict(color=Theme.TEXT_SECONDARY), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=420,
        )
        st.plotly_chart(fig_scatter, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='insight-card'>
            <h4>💡 Key Insight</h4>
            <p>
                Right now we're tracking <span class='highlight'>{ov['total_assets']} different cryptocurrencies</span>
                with a combined value of <span class='highlight'>{format_currency(ov['total_market_value'])}</span>.
                There have been <span class='highlight'>{format_number(ov['total_trades'])} total trades</span>
                at an average price of <span class='highlight'>${ov['average_asset_price']:.2f}</span> per coin.
                Think of this like a stock market report — it shows the overall health of the crypto market.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2: ASSET ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

elif "Asset Analysis" in page:

    st.markdown(f"<h1 style='font-size:2.2rem; margin-bottom:4px;'>📈 Asset Analysis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{Theme.TEXT_SECONDARY}; font-size:1rem; margin-top:0;'>Detailed breakdown from the <code>crypto_summary</code> mart</p>", unsafe_allow_html=True)

    if df_summary_f.empty:
        st.info("No assets match the current filter criteria. Adjust your selection.")
        st.stop()

    # ── Top-level KPI cards ──
    total_val = df_summary_f["total_trade_value"].sum()
    total_vol = df_summary_f["total_volume"].sum()
    total_trd = df_summary_f["number_of_trades"].sum()
    avg_prc = df_summary_f["avg_price"].mean()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Filtered Assets", len(df_summary_f))
    with col2:
        st.metric("Trade Value", format_currency(total_val))
    with col3:
        st.metric("Total Volume", format_number(total_vol))
    with col4:
        st.metric("Average Price", f"${avg_prc:.2f}")

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Bar Chart: Price Range ──
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.markdown(f"<div class='insight-card'><h4>📊 Price Range by Asset</h4>", unsafe_allow_html=True)
        # Use display labels on x-axis
        df_price = df_summary_f.copy()
        df_price["display_label"] = df_price["symbol"].apply(get_short_label)
        fig_price_range = go.Figure()
        fig_price_range.add_trace(go.Bar(
            x=df_price["display_label"],
            y=df_price["max_price"],
            name="Highest Price",
            marker_color=Theme.PRIMARY,
            hovertemplate="<b>%{x}</b><br>Highest: $%{y:,.4f}<extra></extra>",
        ))
        fig_price_range.add_trace(go.Bar(
            x=df_price["display_label"],
            y=df_price["min_price"],
            name="Lowest Price",
            marker_color=Theme.SECONDARY,
            hovertemplate="<b>%{x}</b><br>Lowest: $%{y:,.4f}<extra></extra>",
        ))
        fig_price_range.add_trace(go.Scatter(
            x=df_price["display_label"],
            y=df_price["avg_price"],
            name="Average Price",
            mode="markers+lines",
            marker=dict(color=Theme.WARNING, size=10, symbol="diamond"),
            line=dict(color=Theme.WARNING, width=2, dash="dot"),
            hovertemplate="<b>%{x}</b><br>Average: $%{y:,.4f}<extra></extra>",
        ))
        fig_price_range.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Price per coin in US Dollars", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)", type="log"),
            legend=dict(font=dict(color=Theme.TEXT_SECONDARY), bgcolor="rgba(0,0,0,0)", orientation="h", y=1.1),
            margin=dict(l=10, r=10, t=10, b=10),
            height=420,
        )
        st.plotly_chart(fig_price_range, width='stretch')
        st.markdown("""
        <p class="yaxis-subtitle">💡 The Y-axis shows the price of one coin in US Dollars.
        A higher bar means the coin costs more to buy.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # — Insight in plain language —
        top_traded = df_summary_f.sort_values("number_of_trades", ascending=False).iloc[0]
        top_traded_label = get_short_label(top_traded["symbol"])
        st.markdown(f"""
        <div class='insight-card'>
            <h4>💡 Key Insight</h4>
            <p>
                <span class='highlight'>{top_traded_label}</span> has been the most actively traded,
                with <span class='highlight'>{format_number(top_traded['number_of_trades'])} trades</span>.
                Its average price is <span class='highlight'>${top_traded['avg_price']:.4f}</span>
                and total volume is <span class='highlight'>{format_number(top_traded['total_volume'])}</span>.
                More trades usually means more people are buying and selling — a sign of strong interest.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='insight-card'><h4>📊 Trades per Asset</h4>", unsafe_allow_html=True)
        df_trades = df_summary_f.copy()
        df_trades["display_label"] = df_trades["symbol"].apply(get_short_label)
        fig_trades = px.bar(
            df_trades.sort_values("number_of_trades", ascending=True),
            y="display_label",
            x="number_of_trades",
            color="number_of_trades",
            color_continuous_scale=[Theme.PRIMARY, Theme.SECONDARY],
            orientation="h",
            text="number_of_trades",
            hover_data={
                "number_of_trades": ":,.0f",
                "display_label": False,
            },
        )
        fig_trades.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            marker=dict(line=dict(width=0)),
            hovertemplate="<b>%{customdata[0]}</b><br>Trades: %{x:,.0f}<extra></extra>",
        )
        fig_trades.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="", color=Theme.TEXT_SECONDARY, autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=10, r=60, t=10, b=10),
            height=420,
        )
        st.plotly_chart(fig_trades, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Data Table ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight-card'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📋 Asset Data Table</h4>", unsafe_allow_html=True)

    display_df = df_summary_f.copy()
    display_df["display_label"] = display_df["symbol"].apply(get_short_label)
    display_df["total_trade_value"] = display_df["total_trade_value"].apply(lambda x: f"${x:,.2f}")
    display_df["avg_price"] = display_df["avg_price"].apply(lambda x: f"${x:,.4f}")
    display_df["total_volume"] = display_df["total_volume"].apply(lambda x: f"{x:,}")
    display_df["number_of_trades"] = display_df["number_of_trades"].apply(lambda x: f"{x:,}")
    display_df["max_price"] = display_df["max_price"].apply(lambda x: f"${x:,.4f}")
    display_df["min_price"] = display_df["min_price"].apply(lambda x: f"${x:,.4f}")

    st.dataframe(
        display_df,
        width='stretch',
        column_config={
            "display_label": "Asset",
            "avg_price": "Average Price",
            "max_price": "Highest Price",
            "min_price": "Lowest Price",
            "total_volume": "Total Volume",
            "total_trade_value": "Trade Value",
            "number_of_trades": "Trades",
        },
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3: VOLUME LEADERS
# ═══════════════════════════════════════════════════════════════════════════

elif "Volume Leaders" in page:

    st.markdown(f"<h1 style='font-size:2.2rem; margin-bottom:4px;'>🏆 Volume Leaders</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{Theme.TEXT_SECONDARY}; font-size:1rem; margin-top:0;'>Top assets by trading volume from the <code>top_volume_assets</code> mart</p>", unsafe_allow_html=True)

    if df_top.empty:
        st.info("No volume data available for the current filter criteria.")
        st.stop()

    # ── Top 3 Podium ──
    top_3 = df_top_f.head(3).reset_index(drop=True)
    medals = ["🥇", "🥈", "🥉"]
    border_colors = ["#FFD93D", "#C0C0C0", "#CD7F32"]

    col1, col2, col3 = st.columns(3)
    for i, (_, row) in enumerate(top_3.iterrows()):
        with [col1, col2, col3][i]:
            display_name = get_short_label(row["symbol"])
            st.markdown(f"""
            <div class="podium-card" style="border-color: {border_colors[i]};">
                <div class="medal">{medals[i]}</div>
                <div class="symbol">{display_name}</div>
                <div class="stat-box">
                    <p class="stat-label">Volume</p>
                    <p class="stat-value" style="color: {Theme.TEXT_PRIMARY};">{format_number(row['total_volume'])}</p>
                </div>
                <p class="stat-row">Trade Value: <span style="color: {Theme.SECONDARY};">{format_currency(row['total_trade_value'])}</span></p>
                <p class="stat-row">Trades: <span style="color: {Theme.PRIMARY};">{format_number(row['number_of_trades'])}</span></p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Horizontal Bar Chart + Pie ──
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        st.markdown(f"<div class='insight-card'><h4>📊 All Assets — Volume Comparison</h4>", unsafe_allow_html=True)
        df_sorted = df_top_f.copy()
        df_sorted["display_label"] = df_sorted["symbol"].apply(get_short_label)
        df_sorted = df_sorted.sort_values("total_volume", ascending=True)
        fig_vol = px.bar(
            df_sorted,
            y="display_label",
            x="total_volume",
            color="total_volume",
            color_continuous_scale=[Theme.PRIMARY, Theme.SECONDARY, Theme.WARNING],
            orientation="h",
            text="total_volume",
            hover_data={
                "total_volume": ":,.0f",
                "total_trade_value": ":$,.0f",
                "number_of_trades": ":,.0f",
                "display_label": False,
            },
        )
        fig_vol.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            marker=dict(line=dict(width=0)),
        )
        fig_vol.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Volume", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="", color=Theme.TEXT_SECONDARY, autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=10, r=50, t=10, b=10),
            height=500,
        )
        st.plotly_chart(fig_vol, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='insight-card'><h4>📊 Volume Distribution</h4>", unsafe_allow_html=True)
        df_vol_pie = df_top_f.copy()
        df_vol_pie["display_label"] = df_vol_pie["symbol"].apply(get_short_label)
        fig_vol_pie = px.pie(
            df_vol_pie,
            values="total_volume",
            names="display_label",
            color_discrete_sequence=Theme.CHART_COLORS,
            hole=0.45,
        )
        fig_vol_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color=Theme.TEXT_SECONDARY), orientation="h", y=-0.15),
            margin=dict(l=10, r=10, t=10, b=10),
            height=350,
        )
        fig_vol_pie.update_traces(
            textposition="inside", textinfo="percent+label",
            marker=dict(line=dict(color=Theme.DARK_BG, width=2)),
        )
        st.plotly_chart(fig_vol_pie, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

        # — Insight in plain language —
        if not df_top_f.empty:
            top_vol = df_top_f.iloc[0]
            top_vol_share = top_vol["total_volume"] / df_top_f["total_volume"].sum() * 100
            top_vol_label = get_short_label(top_vol["symbol"])
            st.markdown(f"""
            <div class='insight-card'>
                <h4>💡 Key Insight</h4>
                <p>
                    <span class='highlight'>{top_vol_label}</span> has the highest trading volume at
                    <span class='highlight'>{format_number(top_vol['total_volume'])}</span> —
                    that's <span class='highlight'>{top_vol_share:.1f}%</span> of all the trading happening right now.
                    High volume means lots of people are buying and selling this coin.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ── Full ranking table ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight-card'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📋 Full Volume Ranking</h4>", unsafe_allow_html=True)

    rank_df = df_top_f.copy()
    rank_df.insert(0, "Rank", range(1, len(rank_df) + 1))
    rank_df["display_label"] = rank_df["symbol"].apply(get_short_label)
    rank_df["total_volume"] = rank_df["total_volume"].apply(lambda x: f"{x:,}")
    rank_df["total_trade_value"] = rank_df["total_trade_value"].apply(lambda x: f"${x:,.2f}")
    rank_df["number_of_trades"] = rank_df["number_of_trades"].apply(lambda x: f"{x:,}")

    st.dataframe(
        rank_df,
        width='stretch',
        column_config={
            "Rank": "Rank",
            "display_label": "Asset",
            "total_volume": "Total Volume",
            "total_trade_value": "Trade Value",
            "number_of_trades": "Trades",
        },
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4: PERFORMANCE & VOLATILITY
# ═══════════════════════════════════════════════════════════════════════════

elif "Performance" in page:

    st.markdown(f"<h1 style='font-size:2.2rem; margin-bottom:4px;'>⚡ Performance & Volatility</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{Theme.TEXT_SECONDARY}; font-size:1rem; margin-top:0;'>Risk and performance metrics from the <code>asset_performance</code> mart</p>", unsafe_allow_html=True)

    if df_perf_f.empty:
        st.info("No performance data available for the current filter criteria.")
        st.stop()

    # ── KPIs ──
    avg_volatility = df_perf_f["price_volatility_pct"].mean()
    max_vol_asset = df_perf_f.loc[df_perf_f["price_volatility_pct"].idxmax()]
    min_vol_asset = df_perf_f.loc[df_perf_f["price_volatility_pct"].idxmin()]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average Volatility", f"{avg_volatility:.2f}%")
    with col2:
        st.metric("Most Volatile", f"{get_short_label(max_vol_asset['symbol'])} ({max_vol_asset['price_volatility_pct']:.1f}%)")
    with col3:
        st.metric("Least Volatile", f"{get_short_label(min_vol_asset['symbol'])} ({min_vol_asset['price_volatility_pct']:.1f}%)")
    with col4:
        top_trade_asset = df_perf_f.sort_values("avg_trade_value_per_unit", ascending=False).iloc[0]
        st.metric("Highest Avg Trade Value", get_short_label(top_trade_asset["symbol"]))

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Charts ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"<div class='insight-card'><h4>📊 Price Volatility by Asset</h4>", unsafe_allow_html=True)
        df_vol_sorted = df_perf_f.copy()
        df_vol_sorted["display_label"] = df_vol_sorted["symbol"].apply(get_short_label)
        df_vol_sorted = df_vol_sorted.sort_values("price_volatility_pct", ascending=True)
        fig_volatility = px.bar(
            df_vol_sorted,
            y="display_label",
            x="price_volatility_pct",
            color="price_volatility_pct",
            color_continuous_scale=[Theme.SECONDARY, Theme.WARNING, Theme.ACCENT],
            orientation="h",
            text="price_volatility_pct",
            hover_data={
                "price_volatility_pct": ":.2f",
                "display_label": False,
            },
        )
        fig_volatility.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            marker=dict(line=dict(width=0)),
            hovertemplate="<b>%{customdata[0]}</b><br>Volatility: %{x:.2f}%<extra></extra>",
        )
        fig_volatility.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Volatility (%)", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="", color=Theme.TEXT_SECONDARY, autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=10, r=80, t=10, b=10),
            height=450,
        )
        st.plotly_chart(fig_volatility, width='stretch')
        st.markdown("""
        <p class="yaxis-subtitle">💡 Volatility measures how much a coin's price swings up and down.
        Higher volatility = bigger price moves = higher risk and reward.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<div class='insight-card'><h4>📊 Average Volume per Trade</h4>", unsafe_allow_html=True)
        df_avgt_sorted = df_perf_f.copy()
        df_avgt_sorted["display_label"] = df_avgt_sorted["symbol"].apply(get_short_label)
        df_avgt_sorted = df_avgt_sorted.sort_values("avg_volume_per_trade", ascending=True)
        fig_avgt = px.bar(
            df_avgt_sorted,
            y="display_label",
            x="avg_volume_per_trade",
            color="avg_volume_per_trade",
            color_continuous_scale=[Theme.PRIMARY, Theme.SECONDARY, Theme.WARNING],
            orientation="h",
            text="avg_volume_per_trade",
            hover_data={
                "avg_volume_per_trade": ":,.2f",
                "display_label": False,
            },
        )
        fig_avgt.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside",
            marker=dict(line=dict(width=0)),
            hovertemplate="<b>%{customdata[0]}</b><br>Avg Volume: %{x:,.2f}<extra></extra>",
        )
        fig_avgt.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title="Average Volume per Trade", color=Theme.TEXT_SECONDARY, gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="", color=Theme.TEXT_SECONDARY, autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=10, r=80, t=10, b=10),
            height=450,
        )
        st.plotly_chart(fig_avgt, width='stretch')
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Comprehensive insight card in plain language ──
    max_vol_label = get_short_label(max_vol_asset["symbol"])
    min_vol_label = get_short_label(min_vol_asset["symbol"])
    top_trade_label = get_short_label(top_trade_asset["symbol"])
    st.markdown(f"""
    <div class='insight-card'>
        <h4>🔍 Volatility & Performance Analysis</h4>
        <p>
            On average, the cryptocurrencies you're tracking have a price swing of
            <span class='highlight'>{avg_volatility:.2f}%</span>.
        </p>
        <p>
            <span class='highlight'>{max_vol_label}</span> had the biggest price swing at
            <span class='highlight'>{max_vol_asset['price_volatility_pct']:.2f}%</span>
            (highest price: ${max_vol_asset['max_price']:.4f}, lowest: ${max_vol_asset['min_price']:.4f}).
            This means it's the most exciting — but also the riskiest — coin to own right now.
        </p>
        <p>
            <span class='highlight'>{min_vol_label}</span> is the most stable, with only
            <span class='highlight'>{min_vol_asset['price_volatility_pct']:.2f}%</span> price movement.
            Think of it like a steady stock that doesn't jump around much.
        </p>
        <p>
            When it comes to trade size, <span class='highlight'>{top_trade_label}</span>
            has the highest average trade value at <span class='highlight'>${top_trade_asset['avg_trade_value_per_unit']:.4f}</span> per unit,
            with an average of <span class='highlight'>{format_number(top_trade_asset['avg_volume_per_trade'])}</span> coins per trade.
            Bigger trades often mean larger investors are involved.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Full performance table ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='insight-card'>", unsafe_allow_html=True)
    st.markdown(f"<h4>📋 Full Performance Data</h4>", unsafe_allow_html=True)

    perf_display = df_perf_f.copy()
    perf_display["display_label"] = perf_display["symbol"].apply(get_short_label)
    perf_display["avg_price"] = perf_display["avg_price"].apply(lambda x: f"${x:,.4f}")
    perf_display["price_volatility_pct"] = perf_display["price_volatility_pct"].apply(lambda x: f"{x:.2f}%")
    perf_display["avg_trade_value_per_unit"] = perf_display["avg_trade_value_per_unit"].apply(lambda x: f"${x:,.4f}")
    perf_display["avg_volume_per_trade"] = perf_display["avg_volume_per_trade"].apply(lambda x: f"{x:,.2f}")
    perf_display["max_price"] = perf_display["max_price"].apply(lambda x: f"${x:,.4f}")
    perf_display["min_price"] = perf_display["min_price"].apply(lambda x: f"${x:,.4f}")
    perf_display["total_volume"] = perf_display["total_volume"].apply(lambda x: f"{x:,}")
    perf_display["total_trade_value"] = perf_display["total_trade_value"].apply(lambda x: f"${x:,.2f}")

    st.dataframe(
        perf_display,
        width='stretch',
        column_config={
            "display_label": "Asset",
            "avg_price": "Average Price",
            "max_price": "Highest Price",
            "min_price": "Lowest Price",
            "price_volatility_pct": "Volatility",
            "total_volume": "Volume",
            "total_trade_value": "Trade Value",
            "avg_trade_value_per_unit": "Avg Trade/Unit",
            "avg_volume_per_trade": "Avg Vol/Trade",
        },
        hide_index=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    <p>
        Built with ❤️ using Streamlit · Data sourced from <strong>DBT Marts</strong> on <strong>Databricks SQL Warehouse</strong>
    </p>
    <p style="font-size:0.7rem; margin:4px 0 0 0;">
        Models: market_overview · crypto_summary · top_volume_assets · asset_performance
    </p>
</div>
""", unsafe_allow_html=True)