# Real-Time Financial Market Streaming Lakehouse

## Architecture

Polygon.io
    ↓
Python Producer
    ↓
Azure Event Hubs
    ↓
Azure Databricks
    ↓
ADLS Gen2
    ↓
Bronze
    ↓
Silver
    ↓
Gold
    ↓
dbt
    ↓
Power BI

## Tech Stack

- Python
- Azure Event Hubs
- Azure Databricks
- Delta Lake
- ADLS Gen2
- dbt Core
- Power BI