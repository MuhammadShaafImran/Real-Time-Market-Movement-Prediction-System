import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from datetime import datetime, timedelta

def fetch_yahoo_data(tickers, interval='5m', period='14d'):
    all_data = []
    for symbol in tickers:
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                continue
            df.reset_index(inplace=True)
            time_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            df.rename(columns={
                time_col: 'timestamp', 
                'Open': 'open', 
                'High': 'high', 
                'Low': 'low', 
                'Close': 'close', 
                'Volume': 'volume'
            }, inplace=True)
            df['symbol'] = symbol
            # Keep only required columns
            df = df[['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']]
            # Ensure timestamp is string for parquet
            df['timestamp'] = df['timestamp'].astype(str)
            all_data.append(df)
        except Exception as e:
            print(f"Error fetching Yahoo data for {symbol}: {e}")
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

def save_yahoo_data(df, lookback_days, output_dir):
    if df is None or df.empty:
        return
    os.makedirs(output_dir, exist_ok=True)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    end_str = end_date.strftime('%Y-%m-%d')
    start_str = start_date.strftime('%Y-%m-%d')
    file_path = os.path.join(output_dir, f"{end_str}_{start_str}.parquet")
    
    if os.path.exists(file_path):
        existing_df = pd.read_parquet(file_path)
        combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['timestamp', 'symbol'])
        combined_df.to_parquet(file_path, index=False)
    else:
        df.to_parquet(file_path, index=False)

def load_yahoo_data(path):
    df = pd.read_parquet(path)
    return df
    
if __name__ == '__main__':
    # data = fetch_yahoo_data(['AAPL', 'GOOGL', 'TSLA'])
    # save_yahoo_data(data, './data/raw/yahoo/')
    data = load_yahoo_data('./data/raw/yahoo/2026-05-11_2026-04-27.parquet')
    print(data.head())
    print(data.iloc[0])
    print(data.info())
