"""
API Client for Real-Time Market Movement Prediction System
Handles all communication with the FastAPI backend
"""

import requests
from typing import Dict, List, Any, Optional
import streamlit as st


BASE_URL = "http://127.0.0.1:8000"

# Timeout for API requests (seconds)
REQUEST_TIMEOUT = 10


class APIClient:
    """Client for communicating with the prediction API"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    def _handle_request_error(self, endpoint: str, error: Exception) -> Dict[str, Any]:
        """Handle request errors gracefully"""
        return {
            "status": "error",
            "message": f"Failed to fetch data from {endpoint}: {str(error)}",
            "data": None
        }

    def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/health", e)

    def get_model_info(self) -> Dict[str, Any]:
        """Fetch model information"""
        try:
            response = requests.get(
                f"{self.base_url}/model-info",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/model-info", e)

    def get_metrics(self) -> Dict[str, Any]:
        """Fetch model metrics"""
        try:
            response = requests.get(
                f"{self.base_url}/metrics",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/metrics", e)

    def get_labels(self) -> Dict[str, str]:
        """Fetch prediction labels"""
        try:
            response = requests.get(
                f"{self.base_url}/labels",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/labels", e)

    def get_sample_input(self) -> Dict[str, List[List[float]]]:
        """Fetch sample input data"""
        try:
            response = requests.get(
                f"{self.base_url}/sample-input",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/sample-input", e)

    def get_dataset_info(self) -> Dict[str, Any]:
        """Fetch dataset information"""
        try:
            response = requests.get(
                f"{self.base_url}/dataset-info",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/dataset-info", e)

    def get_latest_market_data(self) -> Dict[str, Any]:
        """Fetch latest market snapshot"""
        try:
            response = requests.get(
                f"{self.base_url}/latest-market-data",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/latest-market-data", e)

    def get_pipeline_status(self) -> Dict[str, str]:
        """Fetch pipeline status"""
        try:
            response = requests.get(
                f"{self.base_url}/pipeline-status",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/pipeline-status", e)

    def get_random_market_sample(self) -> Dict[str, Any]:
        """Fetch a random market sample"""
        try:
            response = requests.get(
                f"{self.base_url}/random-market-sample",
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/random-market-sample", e)

    def predict(self, features: List[List[float]]) -> Dict[str, Any]:
        """Send prediction request"""
        try:
            payload = {"features": features}
            response = requests.post(
                f"{self.base_url}/predict",
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return self._handle_request_error("/predict", e)


# Initialize API client
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()
