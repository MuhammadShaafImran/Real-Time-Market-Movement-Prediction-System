import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from ingestion.yahoo_ingest import fetch_yahoo_data, save_yahoo_data, load_yahoo_data
from ingestion.finnhub_ingest import fetch_finnhub_news, save_finnhub_data, load_finnhub_data
from ingestion.reddit_rss_ingest import fetch_reddit_financial_data, save_reddit_data, load_reddit_data
from ingestion.alpha_vantage_ingest import fetch_alpha_vantage_bulk, save_alpha_vantage_data, load_alpha_vantage_data
from processing.sentiment import SentimentAnalyzer
from processing.feature_engineering import compute_technical_indicators
from processing.aggregate import aggregate_symbol_sentiment, aggregate_reddit_sentiment
from dataset_generator.dataset_builder import build_ml_dataset
from datetime import timedelta
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

load_dotenv()
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
ALPHAVANTAGE_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
YAHOO_RAW_DIR = os.path.join(DATA_DIR, 'raw', 'yahoo')
FINNHUB_RAW_DIR = os.path.join(DATA_DIR, 'raw', 'finnhub')
ALPHA_RAW_DIR = os.path.join(DATA_DIR, 'raw', 'alpha_vantage')
REDDIT_RAW_DIR = os.path.join(DATA_DIR, 'raw', 'reddit')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

TICKERS = ['AAPL', 'GOOGL', 'TSLA']
SUBREDDITS = ['finance', 'investing', 'wallstreetbets']
PRICE_LOOKBACK_DAYS = 60
PRICE_INTERVAL = '5m'
NEWS_LOOKBACK_DAYS = 14
SENTIMENT_FREQ = '1h'
MERGE_TOLERANCE = '1h'
SENTIMENT_MODEL_TYPE = 'finbert'


def _snapshot_parquet_path(directory, lookback_days):
    today = datetime.now()
    lookback_date = today - timedelta(days=lookback_days)
    filename = f"{today.strftime('%Y-%m-%d')}_{lookback_date.strftime('%Y-%m-%d')}.parquet"
    return os.path.join(directory, filename)

def run_pipeline():
    print("1. Running Data Ingestion...")

    # Yahoo Data
    yahoo_path = _snapshot_parquet_path(YAHOO_RAW_DIR, PRICE_LOOKBACK_DAYS)
    if os.path.exists(yahoo_path):
        yahoo_df = load_yahoo_data(yahoo_path)
        print(f"   - Yahoo Data: Loaded from {yahoo_path} ({len(yahoo_df)} records)")
    else:
        yahoo_df = fetch_yahoo_data(TICKERS, interval=PRICE_INTERVAL, period=f'{PRICE_LOOKBACK_DAYS}d')
        save_yahoo_data(yahoo_df, PRICE_LOOKBACK_DAYS, YAHOO_RAW_DIR)
        print(f"   - Yahoo Data: Fetched and saved ({len(yahoo_df)} records)")
    
    # Finnhub Data
    finnhub_path = _snapshot_parquet_path(FINNHUB_RAW_DIR, NEWS_LOOKBACK_DAYS)
    if os.path.exists(finnhub_path):
        finnhub_df = load_finnhub_data(finnhub_path)
        print(f"   - Finnhub Data: Loaded from {finnhub_path} ({len(finnhub_df)} records)")
    else:
        finnhub_df = fetch_finnhub_news(TICKERS, FINNHUB_API_KEY, days_back=NEWS_LOOKBACK_DAYS)
        save_finnhub_data(finnhub_df, NEWS_LOOKBACK_DAYS, FINNHUB_RAW_DIR)
        print(f"   - Finnhub Data: Fetched and saved ({len(finnhub_df)} records)")

    # Alpha Vantage Data
    alpha_path = _snapshot_parquet_path(ALPHA_RAW_DIR, NEWS_LOOKBACK_DAYS)
    if os.path.exists(alpha_path):
        alpha_df = load_alpha_vantage_data(alpha_path)
        print(f"   - Alpha Vantage Data: Loaded from {alpha_path} ({len(alpha_df)} records)")
    else:
        alpha_df = fetch_alpha_vantage_bulk(TICKERS, ALPHAVANTAGE_API_KEY, days_back=NEWS_LOOKBACK_DAYS)
        save_alpha_vantage_data(alpha_df, NEWS_LOOKBACK_DAYS, ALPHA_RAW_DIR)
        print(f"   - Alpha Vantage Data: Fetched and saved ({len(alpha_df)} records)")

    # Reddit Data
    reddit_path = _snapshot_parquet_path(REDDIT_RAW_DIR, NEWS_LOOKBACK_DAYS)
    if os.path.exists(reddit_path):
        reddit_df = load_reddit_data(reddit_path)
        print(f"   - Reddit Data: Loaded from {reddit_path} ({len(reddit_df)} records)")
    else:
        reddit_df = fetch_reddit_financial_data(SUBREDDITS, TICKERS, days_back=NEWS_LOOKBACK_DAYS)
        save_reddit_data(reddit_df, NEWS_LOOKBACK_DAYS, REDDIT_RAW_DIR)
        print(f"   - Reddit Data: Fetched and saved ({len(reddit_df)} records)")
    
    print("2. Running Processing & Feature Engineering...")
    price_features_df = compute_technical_indicators(yahoo_df)
    analyzer = SentimentAnalyzer(model_type=SENTIMENT_MODEL_TYPE)
    
    if not finnhub_df.empty:
        finnhub_df['text'] = finnhub_df['headline'] + " " + finnhub_df['summary']
        finnhub_sentiment_df = analyzer.process_dataframe(finnhub_df, 'text')
    else:
        finnhub_sentiment_df = finnhub_df

    if not alpha_df.empty:
        alpha_df['text'] = alpha_df['headline'] + " " + alpha_df['summary']
        alpha_sentiment_df = analyzer.process_dataframe(alpha_df, 'text')
    else:
        alpha_sentiment_df = alpha_df

    if not reddit_df.empty:
        reddit_df['text'] = reddit_df['headline'] + " " + reddit_df['text']
        reddit_sentiment_df = analyzer.process_dataframe(reddit_df, 'text')
    else:
        reddit_sentiment_df = reddit_df

    print("3. Running Aggregation...")

    symbol_news_df = pd.concat([finnhub_sentiment_df, alpha_sentiment_df], ignore_index=True)
    symbol_news_df['timestamp'] = pd.to_datetime(symbol_news_df['timestamp'], utc=True, errors='coerce')
    symbol_news_df = symbol_news_df.sort_values(['timestamp', 'symbol']).reset_index(drop=True)
    symbol_news_agg_df = aggregate_symbol_sentiment(symbol_news_df, freq=SENTIMENT_FREQ)
    reddit_agg_df = aggregate_reddit_sentiment(reddit_sentiment_df, freq=SENTIMENT_FREQ)
    

    print("4. Building ML-Ready Dataset...")
    ml_dataset = build_ml_dataset(price_features_df, symbol_news_agg_df, reddit_agg_df, merge_tolerance=MERGE_TOLERANCE)
    
    # Save the final dataset
    if not ml_dataset.empty:
        dataset_path = os.path.join(PROCESSED_DIR, f'latest_ml_dataset_v4_{SENTIMENT_MODEL_TYPE}.parquet')
        ml_dataset.to_parquet(dataset_path, index=False)
        print(f"Pipeline Complete. Dataset saved to {dataset_path} with {len(ml_dataset)} records")
    else:
        print("Pipeline Complete. No dataset generated (possibly insufficient data).")

if __name__ == "__main__":
    run_pipeline()
