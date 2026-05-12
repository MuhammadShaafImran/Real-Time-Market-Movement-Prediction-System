import pandas as pd
import numpy as np

def _merge_with_tolerance(left_df, right_df, on, by=None, tolerance='1h'):
    if right_df is None or right_df.empty:
        return left_df
    left = left_df.copy()
    right = right_df.copy()

    left[on] = pd.to_datetime(left[on], utc=True, errors='coerce')
    right[on] = pd.to_datetime(right[on], utc=True, errors='coerce')

    left = left.dropna(subset=[on])
    right = right.dropna(subset=[on])

    if by:
        if by not in left.columns:
            left[by] = None
        if by not in right.columns:
            right[by] = None
        left[by] = left[by].astype(str)
        right[by] = right[by].astype(str)

    if by:
        merged_parts = []
        for grp in left[by].unique():
            left_grp = left[left[by] == grp].sort_values(by=on).reset_index(drop=True)
            right_grp = right[right[by] == grp].sort_values(by=on).reset_index(drop=True)

            if right_grp.empty:
                # no matching right rows for this group; just append left_grp as-is
                merged_parts.append(left_grp)
                continue

            right_merge = right_grp.drop(columns=[by], errors='ignore')

            merged_grp = pd.merge_asof(
                left_grp,
                right_merge,
                on=on,
                direction='backward',
                tolerance=pd.Timedelta(tolerance),
            )
            merged_parts.append(merged_grp)

        if merged_parts:
            return pd.concat(merged_parts, ignore_index=True)
        return left
    
    left = left.sort_values(by=on).reset_index(drop=True)
    right = right.sort_values(by=on).reset_index(drop=True)

    return pd.merge_asof(
        left,
        right,
        on=on,
        direction='backward',
        tolerance=pd.Timedelta(tolerance),
    )


def build_ml_dataset(price_df, symbol_news_df, reddit_agg_df, merge_tolerance='1h'):
    if price_df.empty or symbol_news_df.empty or reddit_agg_df.empty:
        print('Error: One or more input dataframes are empty.')
        return pd.DataFrame()
        
    merged_df = price_df.copy()
    merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'], utc=True)
    
    # Merge ticker-based news on timestamp and symbol 
    symbol_news_df['timestamp'] = pd.to_datetime(symbol_news_df['timestamp'], utc=True)
    merged_df = _merge_with_tolerance(merged_df, symbol_news_df, on='timestamp', by='symbol', tolerance=merge_tolerance)

    # Merge Reddit Data on timestamp only
    reddit_agg_df['timestamp'] = pd.to_datetime(reddit_agg_df['timestamp'], utc=True)
    merged_df = _merge_with_tolerance(merged_df, reddit_agg_df, on='timestamp', tolerance=merge_tolerance)

    sentiment_features = ['ticker_sentiment', 'news_count', 'market_sentiment', 'reddit_hype']
    for col in sentiment_features:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].fillna(0.0)
        else:
            merged_df[col] = 0.0 

    merged_df = merged_df.sort_values(by=['symbol', 'timestamp'])
    
    # Create Target Label (1 if price goes up next hour, 0 if it goes down)
    merged_df['next_close'] = merged_df.groupby('symbol')['close'].shift(-1)
    merged_df['label'] = np.where(merged_df['next_close'] > merged_df['close'], 1, 0)
    merged_df = merged_df.dropna(subset=['next_close']).drop(columns=['next_close'])
    
    return merged_df


if __name__ == "__main__":
    price_df = pd.read_csv('data/raw/price_features.csv', index_col=0)
    symbol_news_df = pd.read_csv('data/raw/symbol_news_agg.csv', index_col=0)
    reddit_agg_df = pd.read_csv('data/raw/reddit_agg.csv', index_col=0)
    ml_dataset = build_ml_dataset(price_df, symbol_news_df, reddit_agg_df)
    print(ml_dataset.head())
    print(ml_dataset.info())