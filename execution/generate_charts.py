import os
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import json

# Set Korean font for Matplotlib
import matplotlib.font_manager as fm

# Explicitly add the font file
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
else:
    # Fallback for other environments
    plt.rcParams['font.family'] = 'sans-serif'

plt.rcParams['axes.unicode_minus'] = False

def generate_stock_charts(data_path=".tmp/market_data.pkl", filtered_csv=".tmp/filtered_stocks.csv"):
    if not os.path.exists(data_path) or not os.path.exists(filtered_csv):
        print("Required data for charts not found.")
        return

    full_df = pd.read_pickle(data_path)
    filtered_df = pd.read_csv(filtered_csv)
    
    # Handle up to 100 stocks
    chart_count = min(len(filtered_df), 100)
    data_to_plot = filtered_df.head(chart_count)
    
    chart_dir = ".tmp/charts"
    if not os.path.exists(chart_dir):
        os.makedirs(chart_dir)
    else:
        for f in os.listdir(chart_dir):
            if f.endswith(".png"):
                os.remove(os.path.join(chart_dir, f))
    
    print(f"Generating charts for {chart_count} stocks...")
    
    mc = mpf.make_marketcolors(up='r', down='b', edge='inherit', wick='inherit', volume='in', ohlc='inherit')
    s  = mpf.make_mpf_style(marketcolors=mc, gridstyle='--', y_on_right=False, rc={'font.family': 'NanumGothic'})

    for idx, row in data_to_plot.iterrows():
        ticker = str(row['code']).zfill(6)
        name = row['name']
        
        ticker_data = full_df[full_df['code'] == ticker].copy()
        if ticker_data.empty: continue
            
        ticker_data = ticker_data.sort_index()
        ticker_data.index = pd.to_datetime(ticker_data.index)
        
        col_map = {'시가': 'Open', '고가': 'High', '저가': 'Low', '종가': 'Close', '거래량': 'Volume'}
        ticker_data = ticker_data.rename(columns=col_map)
        
        plot_data = ticker_data.tail(60)
        if len(plot_data) < 20: continue

        file_path = os.path.join(chart_dir, f"{ticker}.png")
        
        try:
            mpf.plot(plot_data, type='candle', style=s, 
                     mav=(5, 10, 20, 60), 
                     volume=True, 
                     title=f"{name} ({ticker})",
                     savefig=file_path,
                     figsize=(10, 6))
            if (idx + 1) % 20 == 0:
                print(f"Progress: {idx+1}/{chart_count} charts done.")
        except Exception as e:
            print(f"Error generating chart for {name}: {e}")

    print("Chart generation complete.")

if __name__ == "__main__":
    generate_stock_charts()
