# api/app.py

from pathlib import Path
import pandas as pd

from fastapi import FastAPI, HTTPException

from api.schemas import (
    PredictionRequest,
    PredictionResponse
)

from api.predictor import predict


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Real-Time Market Movement Prediction API",
    description="LSTM-based financial market prediction system",
    version="1.0.0"
)


# ============================================================
# LOAD DATASET
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    ROOT_DIR
    / "src"
    / "data"
    / "processed"
    / "latest_ml_dataset_v4_finbert.parquet"
)

dataset_df = pd.read_parquet(DATASET_PATH)


# ============================================================
# ROOT ROUTE
# ============================================================

@app.get("/")
def root():

    return {

        "message": "API is running successfully",

        "project": "Real-Time Market Movement Prediction System",

        "model": "LSTM_Best"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status": "ok",

        "model": "LSTM_Best",

        "api": "running"
    }


# ============================================================
# MODEL INFO
# ============================================================

@app.get("/model-info")
def model_info():

    return {

        "model_name": "LSTM_Best",

        "architecture": "LSTM",

        "sequence_length": 30,

        "input_size": 17,

        "hidden_size": 64,

        "num_layers": 2,

        "dropout": 0.2,

        "optimizer": "Adam",

        "loss_function": "CrossEntropyLoss",

        "epochs": 50,

        "batch_size": 32
    }


# ============================================================
# METRICS
# ============================================================

@app.get("/metrics")
def metrics():

    return {

        "final_test_accuracy": 0.516,

        "final_test_f1_score": 0.475,

        "final_test_rmse": 0.695
    }


# ============================================================
# LABELS
# ============================================================

@app.get("/labels")
def labels():

    return {

        "0": "DOWN",

        "1": "UP"
    }


# ============================================================
# SAMPLE INPUT
# ============================================================

@app.get("/sample-input")
def sample_input():

    sample_features = []

    for _ in range(30):

        row = [0.1] * 17

        sample_features.append(row)

    return {

        "features": sample_features
    }


# ============================================================
# DATASET INFO
# ============================================================

@app.get("/dataset-info")
def dataset_info():

    symbols = []

    if "symbol" in dataset_df.columns:

        symbols = (
            dataset_df["symbol"]
            .dropna()
            .unique()
            .tolist()
        )

    return {

        "total_rows": int(len(dataset_df)),

        "total_features": 17,

        "sequence_length": 30,

        "market_symbols": symbols,

        "data_sources": [

            "Yahoo Finance",

            "Reddit RSS",

            "Finnhub",

            "Alpha Vantage"
        ]
    }


# ============================================================
# LATEST MARKET SNAPSHOT
# ============================================================

@app.get("/latest-market-data")
def latest_market_data():

    latest_row = (
        dataset_df
        .sort_values("timestamp")
        .iloc[-1]
    )

    market_signal = (
        "Bullish"
        if latest_row["label"] == 1
        else "Bearish"
    )

    return {

        "timestamp": str(
            latest_row["timestamp"]
        ),

        "symbol": str(
            latest_row.get("symbol", "UNKNOWN")
        ),

        "close_price": round(
            float(latest_row.get("close", 0)),
            2
        ),

        "RSI": round(
            float(latest_row.get("RSI", 0)),
            2
        ),

        "MACD": round(
            float(latest_row.get("MACD", 0)),
            2
        ),

        "market_sentiment": round(
            float(latest_row.get("market_sentiment", 0)),
            2
        ),

        "reddit_hype": round(
            float(latest_row.get("reddit_hype", 0)),
            2
        ),

        "news_count": int(
            latest_row.get("news_count", 0)
        ),

        "market_signal": market_signal
    }


# ============================================================
# PIPELINE STATUS
# ============================================================

@app.get("/pipeline-status")
def pipeline_status():

    return {

        "data_ingestion": "active",

        "sentiment_analysis": "active",

        "feature_engineering": "active",

        "model_status": "online",

        "api_status": "running"
    }


# ============================================================
# RANDOM MARKET SAMPLE
# ============================================================

@app.get("/random-market-sample")
def random_market_sample():

    sample = dataset_df.sample(1).iloc[0]

    return {

        "timestamp": str(
            sample["timestamp"]
        ),

        "symbol": str(
            sample.get("symbol", "UNKNOWN")
        ),

        "close_price": round(
            float(sample.get("close", 0)),
            2
        ),

        "RSI": round(
            float(sample.get("RSI", 0)),
            2
        ),

        "market_sentiment": round(
            float(sample.get("market_sentiment", 0)),
            2
        ),

        "reddit_hype": round(
            float(sample.get("reddit_hype", 0)),
            2
        )
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict_market(request: PredictionRequest):

    try:

        result = predict(request.features)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )