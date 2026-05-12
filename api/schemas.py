# api/schemas.py

from pydantic import BaseModel, Field
from typing import List


class PredictionRequest(BaseModel):
    """
    Expected input:
    30 timesteps x 17 features
    Shape:
    [
        [17 feature values],
        [17 feature values],
        ...
        total 30 rows
    ]
    """

    features: List[List[float]] = Field(
        ...,
        description="30x17 sequence input for LSTM model"
    )


class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    model: str