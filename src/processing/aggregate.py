import pandas as pd

def aggregate_symbol_sentiment(df, freq='1h'):
    if df is None or df.empty or 'sentiment_score' not in df.columns:
        return pd.DataFrame()
        
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df['timestamp'] = df['timestamp'].dt.floor(freq)
    agg_df = df.groupby(['timestamp', 'symbol']).agg(
        ticker_sentiment=('sentiment_score', 'mean'),
        news_count=('headline', 'count')
    ).reset_index()
    
    return agg_df

def aggregate_finnhub_sentiment(df, freq='1h'):
    return aggregate_symbol_sentiment(df, freq=freq)

def aggregate_reddit_sentiment(df, freq='1h'):
    """Groups Reddit posts by time bucket only (market-wide sentiment)."""
    if df is None or df.empty or 'sentiment_score' not in df.columns:
        return pd.DataFrame()
        
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.floor(freq)
    agg_df = df.groupby('timestamp').agg(
        market_sentiment=('sentiment_score', 'mean'),
        reddit_hype=('headline', 'count')
    ).reset_index()
    
    return agg_df