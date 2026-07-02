# 🚀 Real-Time Financial Streaming Lakehouse

**End-to-end crypto market data pipeline on Azure — from live exchange events to real-time business insights.**

[![Azure](https://img.shields.io/badge/Cloud-Azure-0078D4?logo=microsoftazure&logoColor=white)](https://azure.microsoft.com/)
[![Databricks](https://img.shields.io/badge/Processing-Databricks-FF3621?logo=databricks&logoColor=white)](https://www.databricks.com/)
[![Delta Lake](https://img.shields.io/badge/Storage-Delta%20Lake-00ADD8)](https://delta.io/)
[![dbt](https://img.shields.io/badge/Transform-dbt%20Core-FF694B?logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

This project simulates how a modern data engineering team builds a **production-grade streaming platform** — not just a script that fetches prices, but a full pipeline covering ingestion, real-time processing, storage, transformation, testing, and visualization.

Live crypto trade data streams in from Binance, flows through Azure Event Hubs, gets processed in real time with Databricks Structured Streaming, lands in a Delta Lake Medallion architecture, gets modeled with dbt, and surfaces in an interactive Streamlit dashboard — all within seconds of the trade happening on the exchange.

**Live demo:** [Add your Streamlit dashboard link here]

---

## 🏗️ Architecture

```
Binance WebSocket
      │
      ▼
Python Producer  ──────►  Azure Event Hubs
                                │
                                ▼
                    Azure Databricks (Structured Streaming)
                    watermarking · dedup · window aggregations
                                │
                                ▼
              ┌─────────────────────────────────┐
              │      Delta Lake (Medallion)      │
              │  Bronze → Silver → Gold          │
              │  ADLS Gen2                       │
              └─────────────────────────────────┘
                                │
                                ▼
                          dbt Core
              staging → intermediate → mart models
                       (+ tests, docs, lineage)
                                │
                                ▼
                     Streamlit Dashboard
              real-time KPIs · charts · drilldowns
```

**Storage & Compute layer:** ADLS Gen2 (Delta format) + Databricks SQL Warehouse for analytics

---

## ✨ Key Features

| | |
|---|---|
| ⚡ **Real-time** | Trade data ingested and processed within seconds via structured streaming |
| 📈 **Scalable** | Partitioned, checkpointed pipeline built to handle bursty, high-volume streams |
| ✅ **Reliable** | ACID transactions via Delta Lake, exactly-once processing with idempotent writes |
| 🧱 **Medallion architecture** | Clean separation of raw, cleansed, and business-ready data |
| 🧪 **Tested & documented** | dbt tests + auto-generated lineage and documentation |
| 📊 **Analytics-ready** | Interactive dashboard with KPIs, filters, and drilldowns |

---

## 🧱 Medallion Architecture

| Layer | Purpose | Characteristics |
|---|---|---|
| 🥉 **Bronze** | Raw data, as received | Immutable, append-only, schema-as-received — used for replay/audit/backfill |
| 🥈 **Silver** | Cleansed & enriched | Deduplicated, standardized, business rules applied, joined/enriched |
| 🥇 **Gold** | Business-ready | Aggregated, KPI-calculated, windowed — optimized for reporting and dashboards |

---

## 🔧 Tech Stack

- **Ingestion:** Python, Binance WebSocket API
- **Streaming:** Azure Event Hubs, Azure Databricks Structured Streaming
- **Storage:** Azure Data Lake Storage Gen2, Delta Lake
- **Transformation:** dbt Core
- **Analytics:** Databricks SQL Warehouse
- **Visualization:** Streamlit
- **Language:** Python, SQL

---

## 📊 Dashboard

The Streamlit dashboard provides:

- Real-time KPIs — total market value, total trades, average price
- Portfolio distribution across tracked assets
- Volume vs. trade value trends
- Price volatility by asset
- Filters and drilldowns by asset/time range
- Auto-refresh for live updates

---

## 📂 Project Structure

```
.
├── producer/              # Python WebSocket producer → Event Hubs
├── databricks/            # Structured Streaming notebooks/jobs (Bronze/Silver/Gold)
├── dbt_db/                # dbt project — staging, intermediate, mart models
├── dashboards/streamlit/  # Streamlit dashboard app
├── .streamlit/            # Streamlit configuration
├── .env.example           # Environment variable template
├── requirements.txt       # Python dependencies
└── DEPLOYMENT.md          # Deployment guide
```

---

## 🚀 Getting Started

### Prerequisites
- Azure subscription (Event Hubs, Databricks, ADLS Gen2)
- Python 3.9+
- dbt Core
- Streamlit

### Setup

```bash
# Clone the repo
git clone https://github.com/Sudheendra66/Real-Time-Crypto-Currency-Streaming-Lakehouse.git
cd Real-Time-Crypto-Currency-Streaming-Lakehouse

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Fill in your Azure Event Hubs / Databricks credentials

# Run the producer
python producer/main.py

# Run the dashboard
streamlit run dashboards/streamlit/app.py
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions on Azure.

---

## 🧠 Challenges & Key Learnings

| Challenge | How it was solved |
|---|---|
| High-volume streaming bursts | Partitioning, checkpointing, autoscaling |
| Data quality & duplicates | Watermarking + deduplication logic |
| Schema evolution | Delta Lake + Auto Loader patterns |
| Exactly-once guarantees | Idempotent writes across the pipeline |
| Secure access | Azure Key Vault for credential management |

Building this reinforced that streaming pipelines aren't just about moving data fast — they're about designing for correctness, quality, and reliability as volume and schema evolve.

---

## 🤝 Contributing

This is an open-source learning project — contributions, issues, and suggestions are welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a pull request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — free to use, modify, and distribute.

---

## 👤 Author

**Sudheendra Nekkanti**
Data Engineer | Azure · Databricks · Spark · Delta Lake · dbt

- 🔗 [LinkedIn](#)
- 💻 [GitHub](https://github.com/Sudheendra66)

If you find this project useful, consider giving it a ⭐ — it helps others discover it too!

