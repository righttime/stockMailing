import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_stock_news_naver(stock_code, stock_name):
    """
    Scrapes the latest news for a given stock from Naver Finance.
    """
    url = f"https://finance.naver.com/item/news_news.naver?code={stock_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    news_list = []
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            titles = soup.select('.title a')
            infos = soup.select('.info')
            
            for i in range(min(len(titles), 2)): # Top 2 for space
                title_text = titles[i].get_text(strip=True)
                href = titles[i]['href']
                link = "https://finance.naver.com" + href if href.startswith('/') else href
                source = infos[i].get_text(strip=True) if i < len(infos) else "네이버 금융"
                
                news_list.append({
                    "title": title_text,
                    "link": link,
                    "source": source
                })
    except Exception as e:
        print(f"Error fetching news for {stock_name}: {e}")
    
    if not news_list:
        news_list = [{"title": f"{stock_name} 최신 뉴스 보기", "link": f"https://finance.naver.com/item/news.naver?code={stock_code}", "source": "네이버"}]
        
    return news_list

def gather_all_news(filtered_csv=".tmp/filtered_stocks.csv"):
    if not os.path.exists(filtered_csv):
        print("No filtered stocks found.")
        return
    
    df = pd.read_csv(filtered_csv)
    
    # Increase to 100 as requested
    if len(df) > 100:
        print(f"Limiting to top 100 stocks.")
        df = df.head(100)
    
    all_context = []
    print(f"Gathering news and context for {len(df)} stocks...")
    
    for idx, row in df.iterrows():
        ticker = str(row['code']).zfill(6)
        name = row['name']
        
        news = fetch_stock_news_naver(ticker, name)
        
        # Capture all ranking fields from the row
        item_context = row.to_dict()
        item_context['news'] = news
        item_context['code'] = ticker # Ensure zfill
        
        all_context.append(item_context)
        
        if (idx+1) % 10 == 0:
            print(f"Progress: {idx+1}/{len(df)} info gathered.")
        time.sleep(0.2)
    
    with open(".tmp/news_context.json", "w", encoding="utf-8") as f:
        json.dump(all_context, f, ensure_ascii=False, indent=4)
    print("News and ranking context saved.")

if __name__ == "__main__":
    gather_all_news()
