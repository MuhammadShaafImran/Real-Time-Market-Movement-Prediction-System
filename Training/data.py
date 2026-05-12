from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import torch


def load_parquet(path: Path):
    df = pd.read_parquet(path)
    return df


def preprocess(df: pd.DataFrame):
    df_sorted = df.sort_values('timestamp').reset_index(drop=True)
    y_raw = df_sorted['label'].values
    X = df_sorted.drop(['label', 'timestamp'], axis=1)

    categorical_cols = X.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
    numeric_cols = X.select_dtypes(include=['number']).columns.tolist()

    X_processed = X.copy()
    for col in numeric_cols:
        if X_processed[col].isnull().sum() > 0:
            X_processed[col] = X_processed[col].ffill().bfill().fillna(X_processed[col].mean())

    for col in categorical_cols:
        X_processed[col] = X_processed[col].fillna("Unknown").astype(str)
        X_processed[col] = LabelEncoder().fit_transform(X_processed[col])

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    return X_processed, y, label_encoder


def create_sequences(X: np.ndarray, y: np.ndarray, seq_length=30):
    X_seq, y_seq = [], []
    for i in range(len(X) - seq_length):
        X_seq.append(X[i:i + seq_length])
        y_seq.append(y[i + seq_length])
    return np.array(X_seq), np.array(y_seq)


def split_scale_and_tensorize(X_df, y, seq_length=30, train_frac=0.7, val_frac=0.1):
    n_samples = len(X_df)
    train_size = int(train_frac * n_samples)
    val_size = int(val_frac * n_samples)

    X_train = X_df.iloc[:train_size].values
    y_train = y[:train_size]
    X_val = X_df.iloc[train_size:train_size + val_size].values
    y_val = y[train_size:train_size + val_size]
    X_test = X_df.iloc[train_size + val_size:].values
    y_test = y[train_size + val_size:]

    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    X_train_seq, y_train_seq = create_sequences(X_train_scaled, y_train, seq_length)
    X_val_seq, y_val_seq = create_sequences(X_val_scaled, y_val, seq_length)
    X_test_seq, y_test_seq = create_sequences(X_test_scaled, y_test, seq_length)

    # Convert to torch tensors
    X_train_tensor = torch.FloatTensor(X_train_seq)
    y_train_tensor = torch.LongTensor(y_train_seq)
    X_val_tensor = torch.FloatTensor(X_val_seq)
    y_val_tensor = torch.LongTensor(y_val_seq)
    X_test_tensor = torch.FloatTensor(X_test_seq)
    y_test_tensor = torch.LongTensor(y_test_seq)

    return (X_train_tensor, y_train_tensor,
            X_val_tensor, y_val_tensor,
            X_test_tensor, y_test_tensor,
            scaler)
