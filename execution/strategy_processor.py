import os
import pandas as pd
import numpy as np

def apply_nul_lim_mok_strategy(df):
    """
    Applies the Nul-lim-mok strategy criteria.
    """
    col_map = {
        '시가': '시가', '고가': '고가', '저가': '저가', '종가': '종가', '등락률': '등락률',
        'open': '시가', 'high': '고가', 'low': '저가', 'close': '종가', 'change_rate': '등락률'
    }
    df = df.rename(columns=col_map)
    
    if '종가' not in df.columns or len(df) < 21:
        return False
    
    # Calculate MAs
    df['ma5'] = df['종가'].rolling(window=5).mean()
    df['ma20'] = df['종가'].rolling(window=20).mean()
    
    # Technical conditions
    ma20_upward = df['ma20'].iloc[-1] > df['ma20'].iloc[-2]
    gap_t = abs(df['ma5'].iloc[-1] - df['ma20'].iloc[-1])
    gap_t_1 = abs(df['ma5'].iloc[-2] - df['ma20'].iloc[-2])
    gap_narrowing = gap_t < gap_t_1
    above_ma20 = df['종가'].iloc[-1] > df['ma20'].iloc[-1]
    near_ma20 = (df['종가'].iloc[-1] / df['ma20'].iloc[-1]) < 1.05 # Slightly wider tolerance (5%)
    
    return ma20_upward and gap_narrowing and above_ma20 and near_ma20

def process_strategies(data_path=".tmp/market_data.pkl"):
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}")
        return []

    full_df = pd.read_pickle(data_path)
    tickers_df = pd.read_csv(".tmp/tickers.csv")
    ticker_map = dict(zip(tickers_df['code'].astype(str).str.zfill(6), tickers_df['name']))
    
    # Get the latest day's data for ranking
    latest_date = full_df.index.max()
    latest_market = full_df.loc[latest_date].copy()
    
    # Calculate Global Ranks (Descending order: larger value gets smaller rank number)
    latest_market['rank_change'] = latest_market['등락률'].rank(ascending=False, method='min')
    latest_market['rank_cap'] = latest_market['시가총액'].rank(ascending=False, method='min')
    latest_market['rank_value'] = latest_market['거래대금'].rank(ascending=False, method='min')
    latest_market['total_score'] = latest_market['rank_change'] + latest_market['rank_cap'] + latest_market['rank_value']
    
    # Filter candidates
    candidates = []
    grouped = full_df.groupby('code')
    print(f"Analyzing {len(grouped)} stocks for strategy...")
    
    for code, group in grouped:
        code_str = str(code).zfill(6)
        if apply_nul_lim_mok_strategy(group):
            # Get ranking info from latest_market
            stock_info = latest_market[latest_market['code'] == code]
            if not stock_info.empty:
                info = stock_info.iloc[0]
                candidates.append({
                    "code": code_str,
                    "name": ticker_map.get(code_str, "알수없음"),
                    "price": int(info['종가']),
                    "change": round(float(info['등락률']), 2),
                    "cap": int(info['시가총액']),
                    "value": int(info['거래대금']),
                    "rank_change": int(info['rank_change']),
                    "rank_cap": int(info['rank_cap']),
                    "rank_value": int(info['rank_value']),
                    "total_score": int(info['total_score'])
                })

    # Sort by total_score ascending (lowest score is best)
    sorted_candidates = sorted(candidates, key=lambda x: x['total_score'])
    top_100 = sorted_candidates[:100]
    
    print(f"Found {len(candidates)} matching criteria. Picked Top {len(top_100)} by score.")
    return top_100

if __name__ == "__main__":
    results = process_strategies()
    pd.DataFrame(results).to_csv(".tmp/filtered_stocks.csv", index=False, encoding='utf-8-sig')
    print("Results with ranking saved to .tmp/filtered_stocks.csv")
