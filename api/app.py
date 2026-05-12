# api/app.py

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
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "model": "LSTM_Best"
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