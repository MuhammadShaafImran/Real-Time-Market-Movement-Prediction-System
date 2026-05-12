"""
API Client for Real-Time Market Movement Prediction System
Handles all communication with the FastAPI backend
"""

import requests
from typing import Dict, List, Any
import streamlit as st


BASE_URL = "http://backend:8000"
REQUEST_TIMEOUT = 10


class APIClient:
    """Client for communicating with the prediction API"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def _get(self, endpoint: str) -> Dict[str, Any]:
        """Generic GET request handler"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e), "data": None}

    def _post(self, endpoint: str, payload: Dict) -> Dict[str, Any]:
        """Generic POST request handler"""
        try:
            response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e), "data": None}

    def health_check(self)             -> Dict: return self._get("/health")
    def get_model_info(self)           -> Dict: return self._get("/model-info")
    def get_metrics(self)              -> Dict: return self._get("/metrics")
    def get_labels(self)               -> Dict: return self._get("/labels")
    def get_sample_input(self)         -> Dict: return self._get("/sample-input")
    def get_dataset_info(self)         -> Dict: return self._get("/dataset-info")
    def get_latest_market_data(self)   -> Dict: return self._get("/latest-market-data")
    def get_pipeline_status(self)      -> Dict: return self._get("/pipeline-status")
    def get_random_market_sample(self) -> Dict: return self._get("/random-market-sample")

    def predict(self, features: List[List[float]]) -> Dict:
        return self._post("/predict", {"features": features})


@st.cache_resource
def get_api_client() -> APIClient:
    return APIClient()