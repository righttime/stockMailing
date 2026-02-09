import os
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

def fetch_all_ohlcv(days_back=60):
    """
    Stabilized fetcher using FinanceDataReader (fdr)
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    tmp_dir = ".tmp"
    pkl_path = os.path.join(tmp_dir, "market_data.pkl")
    
    # Check if we already have fresh data for today
    if os.path.exists(pkl_path):
        mtime = datetime.fromtimestamp(os.path.getmtime(pkl_path))
        if mtime.date() == datetime.now().date():
            print(f"Fresh market data found at {pkl_path}. Skipping fetch.")
            return

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    print(f"Fetching market symbols (KOSPI & KOSDAQ)...")
    try:
        # Get list of all stocks
        df_kospi = fdr.StockListing('KOSPI')
        df_kosdaq = fdr.StockListing('KOSDAQ')
        df_list = pd.concat([df_kospi, df_kosdaq])
        
        # Save ticker info for mapping
        ticker_info = df_list[['Code', 'Name', 'Marcap']].rename(columns={
            'Code': 'code', 
            'Name': 'name',
            'Marcap': '시가총액'
        })
        ticker_info.to_csv(os.path.join(tmp_dir, "tickers.csv"), index=False)
        print(f"Found {len(ticker_info)} tickers.")
        
        # Create marcap mapping
        marcap_map = dict(zip(ticker_info['code'], ticker_info['시가총액']))
    except Exception as e:
        print(f"Error getting ticker list: {e}")
        return

    # To scan the whole market but keep it fast, we identify business days
    sample = fdr.DataReader('005930', start_date, end_date)
    business_days = sample.index.strftime("%Y-%m-%d").tolist()
    print(f"Business days identified: {len(business_days)}")

    # Fetch all tickers in the market
    target_codes = ticker_info['code'].tolist()
    
    data_list = []
    print(f"Fetching OHLCV for {len(target_codes)} stocks...")
    
    for i, code in enumerate(target_codes):
        if i % 100 == 0: print(f"Processing... {i}/{len(target_codes)}")
        try:
            df = fdr.DataReader(code, start_date, end_date)
            if not df.empty:
                df['code'] = code
                # Calculate required columns for strategy_processor
                df['등락률'] = df['Change'] * 100
                df['시가총액'] = marcap_map.get(code, 0)
                df['거래대금'] = df['Close'] * df['Volume']
                
                # Rename standard columns
                df.rename(columns={
                    'Open': '시가', 'High': '고가', 'Low': '저가', 'Close': '종가', 'Volume': '거래량'
                }, inplace=True)
                data_list.append(df)
        except:
            continue
            
    if data_list:
        full_df = pd.concat(data_list)
        full_df.index.name = '날짜'
        full_df.to_pickle(os.path.join(tmp_dir, "market_data.pkl"))
        print(f"Saved {len(full_df)} rows to .tmp/market_data.pkl")
    else:
        print("No data fetched.")

if __name__ == "__main__":
    fetch_all_ohlcv()
