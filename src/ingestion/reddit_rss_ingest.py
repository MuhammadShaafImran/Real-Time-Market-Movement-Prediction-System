import os
import time  # Added to handle rate limiting
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import feedparser

def fetch_reddit_financial_data(subreddits, tickers=['AAPL', 'GOOGL', 'TSLA'], days_back=14):
    all_posts = []
    # Using timezone-aware UTC now for consistency across all data sources
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - pd.Timedelta(days=days_back)
    
    # Mapping common names to tickers to improve detection
    name_map = {'APPLE': 'AAPL', 'GOOGLE': 'GOOGL', 'ALPHABET': 'GOOGL', 'TESLA': 'TSLA', 'ELON': 'TSLA'}
    
    headers = {'User-Agent': 'MarketMonitor/1.0 by DataPipeline'}
    
    for sub in subreddits:
        url = f'https://www.reddit.com/r/{sub}/.rss'
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                for entry in feed.entries:
                    # 1. Clean up the HTML from the RSS summary
                    summary = getattr(entry, "summary", "")
                    soup = BeautifulSoup(str(summary), 'html.parser')
                    text_content = soup.get_text(separator=' ').strip()
                    full_text = f"{entry.title} {text_content}".upper()

                    # 2. Extract Timestamp and check against cutoff
                    updated_str = getattr(entry, "updated", None)
                    if not updated_str:
                        print('error in time format [reddit]')
                        continue
                    entry_timestamp = pd.to_datetime(updated_str, utc=True, errors='coerce')
                    
                    if pd.isna(entry_timestamp) or entry_timestamp < cutoff:
                        continue

                    # 3. Ticker Extraction Logic
                    # We check if the post mentions our specific tickers or their company names
                    detected_tickers = []
                    for t in tickers:
                        if t in full_text: # Matches '$TSLA' or 'TSLA'
                            detected_tickers.append(t)
                    
                    for name, ticker in name_map.items():
                        if name in full_text:
                            detected_tickers.append(ticker)
                    
                    detected_tickers = list(set(detected_tickers)) # Remove duplicates

                    # 4. Data Structuring
                    # If no specific ticker is found, label as 'GENERAL'
                    if not detected_tickers:
                        detected_tickers = ['GENERAL']

                    for symbol in detected_tickers:
                        all_posts.append({
                            'timestamp': entry_timestamp.isoformat(),
                            'symbol': symbol,
                            'source': f"reddit/r/{sub}",
                            'headline': entry.title,
                            'text': text_content
                        })
            else:
                print(f"Error {response.status_code} for r/{sub}")
                
        except Exception as e:
            print(f"Failed to fetch r/{sub}: {e}")
            
        # Respect Reddit's rate limits
        time.sleep(2)
                
    df = pd.DataFrame(all_posts)
    return df

def save_reddit_data(df, lookback_days, output_dir):
    if df is None or df.empty:
        print("No data to save.")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    end_str = end_date.strftime('%Y-%m-%d')
    start_str = start_date.strftime('%Y-%m-%d')
    file_path = os.path.join(output_dir, f"{end_str}_{start_str}.parquet")
    
    if os.path.exists(file_path):
        existing_df = pd.read_parquet(file_path)
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['timestamp', 'subreddit', 'title'])
        combined_df.to_parquet(file_path, index=False)
    else:
        df.to_parquet(file_path, index=False)
    
    print(f"Data successfully saved to {file_path}")

def load_reddit_data(path):
    df = pd.read_parquet(path)
    return df

if __name__ == '__main__':
    # Added 'wallstreetbets' if you want market talks!
    # subreddits = ['finance', 'investing', 'wallstreetbets']
    # target_tickers = ['AAPL', 'GOOGL', 'TSLA']
    # target_subs = ['wallstreetbets', 'stocks', 'investing', 'finance']
    
    # reddit_data = fetch_reddit_financial_data(target_subs, tickers=target_tickers)
    # save_reddit_data(reddit_data, 'data/raw/reddit/')
    data = load_reddit_data('./data/raw/reddit/2026-05-12_2026-04-28.parquet')
    print(data.head())
    print(data.iloc[0])
    print(data.info())