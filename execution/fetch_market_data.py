import os
import pandas as pd
from pykrx import stock
from datetime import datetime, timedelta
import time

def fetch_all_ohlcv(days_back=60):
    """
    Optimized fetcher: Gets market-wide data using get_market_ohlcv.
    """
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
    
    tmp_dir = ".tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    print(f"Fetching business days between {start_date} and {end_date}...")
    try:
        # Get business days using a representative ticker
        sample_df = stock.get_market_ohlcv_by_date(start_date, end_date, "005930")
        if sample_df.empty:
            print("No business days found in range.")
            return
        business_days = sample_df.index.strftime("%Y%m%d").tolist()
    except Exception as e:
        print(f"Error getting business days: {e}")
        return

    print(f"Total business days to fetch: {len(business_days)}")
    
    # Save ticker names for mapping
    print("Fetching ticker names...")
    tickers_kospi = stock.get_market_ticker_list(market="KOSPI")
    tickers_kosdaq = stock.get_market_ticker_list(market="KOSDAQ")
    all_tickers = list(set(tickers_kospi + tickers_kosdaq))
    
    ticker_info = []
    # Fetch names in chunks or as a dict
    for ticker in all_tickers:
        name = stock.get_market_ticker_name(ticker)
        ticker_info.append({"code": ticker, "name": name})
    pd.DataFrame(ticker_info).to_csv(os.path.join(tmp_dir, "tickers.csv"), index=False)

    data_list = []
    
    for date in business_days:
        print(f"Fetching data for {date}...", end=" ", flush=True)
        try:
            # get_market_ohlcv is the correct and robust function for market-wide data on a date
            df_kospi = stock.get_market_ohlcv(date, market="KOSPI")
            df_kosdaq = stock.get_market_ohlcv(date, market="KOSDAQ")
            
            day_df = pd.concat([df_kospi, df_kosdaq])
            
            if day_df.empty:
                print("Empty.")
                continue
                
            day_df['날짜'] = pd.to_datetime(date)
            # Ticker index is named '티커' after concat usually, or just an anonymous index
            day_df.reset_index(inplace=True)
            # Rename for strategy_processor
            if '티커' in day_df.columns:
                day_df.rename(columns={'티커': 'code'}, inplace=True)
            elif 'index' in day_df.columns:
                day_df.rename(columns={'index': 'code'}, inplace=True)
            
            data_list.append(day_df)
            print("Done.")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(0.3) 

    if data_list:
        full_df = pd.concat(data_list)
        full_df.set_index('날짜', inplace=True)
        full_df.to_pickle(os.path.join(tmp_dir, "market_data.pkl"))
        print(f"\nSaved {len(full_df)} rows to {os.path.join(tmp_dir, 'market_data.pkl')}")
    else:
        print("\nNo data fetched.")

if __name__ == "__main__":
    fetch_all_ohlcv()
