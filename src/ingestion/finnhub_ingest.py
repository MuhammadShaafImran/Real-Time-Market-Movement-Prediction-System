import os
import pandas as pd
import finnhub
from datetime import datetime, timedelta
import dotenv

dotenv.load_dotenv()

import time
import pandas as pd
import finnhub
from datetime import datetime, timedelta, timezone

def fetch_finnhub_news(tickers, api_key, days_back=14):
    if not api_key:
        print("Finnhub API key not found")
        return pd.DataFrame()
        
    client = finnhub.Client(api_key=api_key)
    
    # 1. Define UTC Timestamps for alignment
    now_utc = datetime.now(timezone.utc)
    start_date_str = (now_utc - timedelta(days=days_back)).strftime('%Y-%m-%d')
    end_date_str = now_utc.strftime('%Y-%m-%d')
    cutoff_timestamp = int((now_utc - timedelta(days=days_back)).timestamp())
    
    all_news = []
    
    # --- Company News (Supports Date Filtering) ---
    for symbol in tickers:
        try:
            print(f"Fetching news for {symbol}...")
            news = client.company_news(symbol, _from=start_date_str, to=end_date_str)
            
            for item in news:
                all_news.append({
                    # Store as UTC ISO for easy Pandas merging later
                    'timestamp': datetime.fromtimestamp(item['datetime'], tz=timezone.utc).isoformat(),
                    'unix_time': item['datetime'],
                    'source': item['source'],
                    'headline': item['headline'],
                    'summary': item['summary'],
                    'symbol': symbol,
                    'category': item.get('category', 'company')
                })
            
            # 2. Rate Limit Protection: Finnhub allows 60 calls/min on free tier. 
            # A small sleep ensures we don't get blocked if the ticker list grows.
            time.sleep(1.1) 
            
        except Exception as e:
            print(f"Error fetching company news for {symbol}: {e}")
            
    # --- General News (Manual Date Filtering Required) ---
    try:
        print("Fetching general market news...")
        general_news = client.general_news('general', min_id=0)
        
        for item in general_news:
            # 3. Manual Filter: General news endpoint doesn't accept date params
            if item['datetime'] >= cutoff_timestamp:
                all_news.append({
                    'timestamp': datetime.fromtimestamp(item['datetime'], tz=timezone.utc).isoformat(),
                    'unix_time': item['datetime'],
                    'source': item['source'],
                    'headline': item['headline'],
                    'summary': item['summary'],
                    'symbol': 'GENERAL',
                    'category': item.get('category', 'general')
                })
    except Exception as e:
        print(f"Error fetching general news: {e}")
        
    df = pd.DataFrame(all_news)
    
    if not df.empty:
        # Sort by time so the sequential model gets data in order
        df = df.sort_values('unix_time').drop_duplicates(subset=['headline', 'symbol'])
        return df[['timestamp', 'symbol', 'source', 'headline', 'summary']]
    
    return df

def save_finnhub_data(df, days_back, output_dir):
    if df is None or df.empty:
        return
    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    file_path = os.path.join(output_dir, f"{end_date}_{start_date}.parquet")
    
    if os.path.exists(file_path):
        existing_df = pd.read_parquet(file_path)
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['timestamp', 'headline', 'symbol'])
        combined_df.to_parquet(file_path, index=False)
    else:
        df.to_parquet(file_path, index=False)

def load_finnhub_data(path):
    df = pd.read_parquet(path)
    return df

if __name__ == '__main__':
    # api_key = os.getenv('FINNHUB_API_KEY')
    # tickers = ['AAPL', 'GOOGL', 'TSLA']
    # data = fetch_finnhub_news(tickers, api_key)
    # save_finnhub_data(data, 14, './data/raw/finnhub/')
    data = pd.read_parquet('./data/raw/finnhub/2026-05-11_2026-04-27.parquet')
    print(data.head())
    print(data.iloc[0])
    print(data.info())