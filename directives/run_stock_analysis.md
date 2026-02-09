# SOP: Daily Stock Analysis & Report

## Goal
To analyze the Korean stock market daily, identify stocks in "Nul-lim-mok" patterns, and send a consolidated report to `eyedoloveu@gmail.com`.

## Inputs
- `credentials.json`: Google OAuth credentials (required for Gmail API).
- Internet connection for stock data and news.

## Workflow Step-by-Step

### 1. Fetch Market Data
Run the fetching script to download OHLCV data for KOSPI and KOSDAQ.
```powershell
python execution/fetch_market_data.py
```
*Outputs stored in `.tmp/market_data.pkl`.*

### 2. Apply Analysis Strategy
Process the downloaded data using technical indicators to filter stocks.
```powershell
python execution/strategy_processor.py
```
*Outputs filtered list to `.tmp/filtered_stocks.csv`.*

### 3. Gather News & Context
Search for news and information regarding the filtered stocks.
```powershell
python execution/search_news.py
```
*Outputs context to `.tmp/news_context.json`.*

### 4. Send Email Report
Format the collected information into an HTML email and send it via Gmail.
```powershell
python execution/gmail_sender.py
```

## Troubleshooting
- **No data found**: Check if the market was open or if `pykrx` is blocked.
- **Gmail Auth Error**: Ensure `credentials.json` is present and `token.json` is refreshed.
- **Performance**: Fetching 2500+ stocks can be slow; ensure the script completes before timeout.

## Maintenance
- To update the "Nul-lim-mok" criteria, modify the logic in `execution/strategy_processor.py`.
