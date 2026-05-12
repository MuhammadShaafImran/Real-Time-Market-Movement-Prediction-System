import os
from datetime import datetime, timedelta, timezone
import pandas as pd
import requests
import time
from dotenv import load_dotenv

load_dotenv()
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


def _parse_alpha_timestamp(value):
    if not value:
        return pd.NaT
    # Alpha Vantage format: 20231015T143000
    try:
        parsed = pd.to_datetime(value, format="%Y%m%dT%H%M%S", utc=True)
    except:
        parsed = pd.to_datetime(value, utc=True, errors="coerce")
    return parsed

def fetch_alpha_vantage_news(tickers, api_key, days_back=14, limit=1000):
    """
    Enhanced fetcher that extracts built-in sentiment scores and handles rate limits.
    """
    if not api_key:
        print("Alpha Vantage API key not found")
        return pd.DataFrame()
    
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ",".join(tickers),
        "sort": "LATEST",
        "limit": limit,
        "apikey": api_key,
    }

    # Set UTC time range
    now_utc = datetime.now(timezone.utc)
    start_time = now_utc - timedelta(days=days_back)
    params["time_from"] = start_time.strftime("%Y%m%dT%H%M")

    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()

        if "Information" in payload and "rate limit" in payload["Information"].lower():
            print("Alpha Vantage Rate Limit Hit. Waiting 60 seconds...")
            time.sleep(60)
            return fetch_alpha_vantage_news(tickers, api_key, days_back, limit)

    except Exception as exc:
        print(f"Error fetching Alpha Vantage news: {exc}")
        return pd.DataFrame()

    feed = payload.get("feed", [])
    all_news = []
    valid_tickers = {ticker.upper() for ticker in tickers}

    for item in feed:
        published = _parse_alpha_timestamp(item.get("time_published"))
        
        # Filter by date manually just in case the API returned extra
        if pd.isna(published) or published < start_time:
            continue

        # Alpha Vantage provides sentiment per ticker per article
        ticker_sentiment_list = item.get("ticker_sentiment", []) or []
        
        for ts_item in ticker_sentiment_list:
            symbol = str(ts_item.get("ticker", "")).upper()
            
            if symbol in valid_tickers:
                all_news.append({
                    "timestamp": published.isoformat(),
                    "symbol": symbol,
                    "source": "alpha_vantage",
                    "headline": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    # NEW: Captured sentiment metrics
                    "sentiment_score": float(ts_item.get("ticker_sentiment_score", 0)),
                    "sentiment_label": ts_item.get("ticker_sentiment_label", "Neutral"),
                    "relevance_score": float(ts_item.get("relevance_score", 0)),
                    "url": item.get("url", "")
                })

    df = pd.DataFrame(all_news)
    
    if not df.empty:
        # Standardize column order for merging with Reddit/Finnhub later
        df = df.sort_values("timestamp")
        return df[["timestamp", "symbol", "source", "headline", "sentiment_score", "sentiment_label", "url"]]
    
    return df

def fetch_alpha_vantage_bulk(tickers, api_key, days_back=14):
    """
    Fetches both ticker-specific and topic-specific news to maximize dataset size.
    """
    if not api_key:
        print("API Key missing.")
        return pd.DataFrame()

    all_results = []
    now_utc = datetime.now(timezone.utc)
    start_time_str = (now_utc - timedelta(days=days_back)).strftime("%Y%m%dT%H%M")

    # 'technology' and 'financial_markets'
    topic_params = {
        "function": "NEWS_SENTIMENT",
        "topics": "technology,financial_markets,economy_macro",
        "sort": "LATEST",
        "limit": 1000,
        "time_from": start_time_str,
        "apikey": api_key
    }
    
    # Ticker Fetch 
    ticker_params = {
        "function": "NEWS_SENTIMENT",
        "tickers": ",".join(tickers),
        "sort": "LATEST",
        "limit": 1000,
        "time_from": start_time_str,
        "apikey": api_key
    }

    # Helper to process the API response
    def process_payload(params):
        try:
            resp = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=20)
            data = resp.json()
            if "feed" in data:
                return data["feed"]
            if "Information" in data:
                print(f"API Note: {data['Information']}")
            return []
        except Exception as e:
            print(f"Request failed: {e}")
            return []

    # Fetch both (Note: This uses 2 of your 25 daily calls)
    print("Fetching broad market news...")
    all_results.extend(process_payload(topic_params))
    
    time.sleep(1) # Small delay to be safe
    
    print(f"Fetching specific news for {tickers}...")
    all_results.extend(process_payload(ticker_params))

    # --- Step 3: Parse and Structure ---
    processed_rows = []
    seen_articles = set() # To avoid double-counting articles that hit both filters

    for item in all_results:
        url = item.get("url")
        if url in seen_articles: continue
        seen_articles.add(url)

        # Standard info
        base_data = {
            "timestamp": pd.to_datetime(item.get("time_published"), format="%Y%m%dT%H%M%S", utc=True),
            "headline": item.get("title"),
            "summary": item.get("summary"),
            "overall_sentiment": item.get("overall_sentiment_score")
        }

        # Extract per-ticker scores
        ticker_data = item.get("ticker_sentiment", [])
        if ticker_data:
            for t_info in ticker_data:
                symbol = t_info.get("ticker")
                # We keep the row if it's one of our target stocks
                if symbol in tickers:
                    row = base_data.copy()
                    row.update({
                        "symbol": symbol,
                        "sentiment_score": float(t_info.get("ticker_sentiment_score", 0)),
                        "relevance": float(t_info.get("relevance_score", 0))
                    })
                    processed_rows.append(row)
        else:
            # If no specific ticker, label as GENERAL context
            row = base_data.copy()
            row.update({"symbol": "GENERAL", "sentiment_score": base_data["overall_sentiment"], "relevance": 1.0})
            processed_rows.append(row)

    df = pd.DataFrame(processed_rows)
    print(f"Total rows collected: {len(df)}")
    return df

def save_alpha_vantage_data(df, days_back, output_dir):
    if df is None or df.empty:
        return

    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    file_path = os.path.join(output_dir, f"{end_date}_{start_date}.parquet")

    if os.path.exists(file_path):
        existing_df = pd.read_parquet(file_path)
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=["timestamp", "headline", "symbol"])
        combined_df.to_parquet(file_path, index=False)
    else:
        df.to_parquet(file_path, index=False)

def load_alpha_vantage_data(path):
    return pd.read_parquet(path)


if __name__ == "__main__":
    # api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    # tickers = ["AAPL", "GOOGL", "TSLA"]
    # data = fetch_alpha_vantage_bulk(tickers, api_key)
    # save_alpha_vantage_data(data, 14, "./data/raw/alpha_vantage/")
    data = pd.read_parquet('./data/raw/alpha_vantage/2026-05-12_2026-04-28.parquet')
    print(data.head())
    print(data.iloc[0])
    print(data.info())