# Streamlit Community Cloud Deployment Guide

This guide explains how to deploy the Crypto & Gold Market Intelligence dashboard to Streamlit Community Cloud.

## Prerequisites

- A GitHub account with this repository pushed
- A Databricks SQL Warehouse running and accessible
- DBT models deployed to Databricks (market_overview, crypto_summary, top_volume_assets)

## Step 1: Prepare Your Repository

Ensure these files are committed to GitHub:

```
financial-streaming-lakehouse/
├── dashboards/
│   └── streamlit/
│       ├── app.py              # Main Streamlit app
│       ├── config.py           # Configuration (uses st.secrets)
│       ├── db_connector.py     # Databricks connection
│       └── data/               # Optional local data
├── .streamlit/
│   └── secrets.toml.example    # Template for secrets
├── requirements.txt            # Python dependencies
├── .gitignore                  # Ensures secrets are not committed
└── DEPLOYMENT.md              # This file
```

**Important:** The file `.streamlit/secrets.toml` should NEVER be committed to GitHub. It is already in `.gitignore`.

## Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository: `your-username/financial-streaming-lakehouse`
4. Set the **Main file path** to:
   ```
   dashboards/streamlit/app.py
   ```
5. Click **"Deploy!"**

## Step 3: Configure Secrets

After deployment starts (or fails), you need to add your Databricks credentials:

1. In your app dashboard, click the **"Settings"** gear icon (or "Manage app")
2. Go to the **"Secrets"** tab
3. Paste the following TOML configuration, replacing with your actual values:

```toml
[databricks]
server_hostname = "your-workspace.azuredatabricks.net"
http_path = "/sql/1.0/warehouses/your-warehouse-id"
access_token = "dapi-your-databricks-access-token"
catalog = "hive_metastore"
schema = "default"
```

4. Click **"Save"**

The app will automatically restart with the new secrets.

## Step 4: Verify Databricks SQL Warehouse

Ensure your Databricks SQL Warehouse is:

1. **Running** - Not suspended
2. **Accessible** - The server hostname and HTTP path are correct
3. **Has the required tables:**
   - `market_overview`
   - `crypto_summary`
   - `top_volume_assets`

You can find your SQL Warehouse details in the Databricks workspace:
- **Server Hostname:** Found in "SQL Warehouses" → Your Warehouse → "Connection Details"
- **HTTP Path:** Found in the same location
- **Access Token:** Generate a new token in Databricks workspace → "User Settings" → "Access Tokens"

## Step 5: Test the Deployment

Once deployed, the app should:

1. Load without errors
2. Display the "Market Overview" page with crypto data
3. Allow navigation between pages (Asset Analysis, Volume Leaders, Performance)
4. Respond to sidebar filters

### Common Issues

**Issue: "Missing Databricks Configuration"**
- **Solution:** Add the secrets in Streamlit Cloud dashboard (Step 3)

**Issue: "Databricks connection failed"**
- **Solution:** 
  - Verify SQL Warehouse is running
  - Check server_hostname and http_path are correct
  - Ensure access token is valid and not expired
  - Verify tables exist in the specified catalog/schema

**Issue: "Module not found"**
- **Solution:** Check `requirements.txt` is in the repository root and all dependencies are listed

## Local Development

To run locally:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.streamlit/secrets.toml` from the example:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
5. Edit `.streamlit/secrets.toml` with your actual Databricks credentials
6. Run the app:
   ```bash
   cd dashboards/streamlit
   streamlit run app.py
   ```

## Security Notes

- **Never commit secrets** to version control
- Use Streamlit Cloud's built-in secrets manager for production
- Rotate access tokens regularly
- Use fine-grained access tokens with minimal permissions
- The `.streamlit/secrets.toml` file is gitignored to prevent accidental commits

## Updating the App

To update the deployed app:

1. Push changes to your GitHub repository
2. Streamlit Cloud will automatically redeploy (if auto-deploy is enabled)
3. Or manually trigger a redeploy from the Streamlit Cloud dashboard

## Support

For issues with:
- **Streamlit Cloud:** Check [docs.streamlit.io](https://docs.streamlit.io/streamlit-community-cloud)
- **Databricks SQL:** Check [docs.databricks.com](https://docs.databricks.com/sql/index.html)
- **DBT Models:** Check your dbt project documentation