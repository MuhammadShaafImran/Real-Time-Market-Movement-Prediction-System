import pandas as pd
import ta
from ingestion.yahoo_ingest import load_yahoo_data
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands

def compute_technical_indicators(df):
    """
    Compute technical indicators for price data.
    Handles multiple stocks if 'symbol' column is present.
    """
    if df is None or df.empty:
        return df
        
    # If multiple symbols are present, process each group independently
    if 'symbol' in df.columns and df['symbol'].nunique() > 1:
        return df.groupby('symbol', group_keys=False).apply(compute_technical_indicators)
        
    df = df.copy()
    
    # Sort by timestamp to ensure calculations are correct
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
            
    # RSI
    df['RSI'] = RSIIndicator(
        close=df['close'],
        window=14
    ).rsi()

    # MACD
    macd = MACD(close=df['close'])

    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()

    # Moving averages
    df['SMA_20'] = SMAIndicator(
        close=df['close'],
        window=20
    ).sma_indicator()

    df['EMA_20'] = EMAIndicator(
        close=df['close'],
        window=20
    ).ema_indicator()

    # Bollinger Bands
    bb = BollingerBands(
        close=df['close'],
        window=20,
        window_dev=2
    )

    df['BB_high'] = bb.bollinger_hband()
    df['BB_low'] = bb.bollinger_lband()
    
    return df

if __name__ == "__main__":
    yahoo_df = load_yahoo_data('./data/raw/yahoo/2026-05-11_2026-04-27.parquet')
    processed = compute_technical_indicators(yahoo_df)
    processed.to_csv('./data/processed/yahoo-2026-05-11_2026-04-27.csv')