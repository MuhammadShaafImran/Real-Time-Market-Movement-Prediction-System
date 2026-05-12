# Real-Time Market Movement Prediction System - Streamlit Frontend

## Overview

Professional Streamlit dashboard frontend for the Real-Time Market Movement Prediction System. Connects to the FastAPI backend and displays:

- **System Status Monitoring**: Real-time API, Model, and Pipeline status
- **Model Performance Metrics**: Accuracy, F1 Score, and RMSE
- **Latest Market Snapshot**: Current price, technical indicators, and sentiment analysis
- **Dataset Information**: Dataset stats and data sources
- **Prediction Interface**: Generate predictions using sample or custom data
- **Model Architecture Details**: Complete model configuration

## Prerequisites

- Python 3.8+
- FastAPI backend running at `http://127.0.0.1:8000`

## Installation

1. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv frontend_env
   source frontend_env/Scripts/activate  # On Windows
   # or
   source frontend_env/bin/activate      # On macOS/Linux
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Frontend

1. **Make sure the FastAPI backend is running**:
   ```bash
   cd ../api
   uvicorn app:app --reload --port 8000
   ```

2. **In a new terminal, run the Streamlit app**:
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. **Open your browser** to:
   ```
   http://localhost:8501
   ```

## Features

### 🎨 Clean, Professional UI
- Modern dashboard layout with intuitive organization
- Status indicators for system components
- Color-coded signals (Green = Active/Bullish, Red = Inactive/Bearish)
- Responsive columns and sections

### 📊 Real-Time Metrics
- Model performance metrics displayed with precision formatting
- Latest market data including technical indicators (RSI, MACD)
- Sentiment analysis scores from Reddit and news sources

### 🔮 Prediction Engine
- One-click prediction generation
- Automatic sample input fetching
- Confidence score display
- Clear indication of market direction (UP/DOWN)

### 📁 Dataset & Model Info
- Dataset statistics (total rows, features, sequence length)
- Market symbols coverage
- Data sources (Yahoo Finance, Reddit, Finnhub, Alpha Vantage)
- Complete model architecture details

### 🛡️ Error Handling
- Graceful API failure handling
- User-friendly error messages
- Fallback values for missing data

## Architecture

```
frontend/
├── app.py           # Main Streamlit application
├── api_client.py    # API communication layer
├── requirements.txt # Python dependencies
└── README.md        # This file
```

### `api_client.py`
Encapsulates all API communication with the backend:
- `health_check()` - Check API status
- `get_model_info()` - Fetch model architecture
- `get_metrics()` - Fetch performance metrics
- `get_latest_market_data()` - Get current market snapshot
- `get_dataset_info()` - Get dataset information
- `get_pipeline_status()` - Check pipeline status
- `predict()` - Send prediction request

### `app.py`
Streamlit frontend with:
- Page configuration and styling
- Sidebar status indicators
- Dashboard sections for each feature
- Error handling and user feedback

## Configuration

### Backend URL
To connect to a different backend instance, modify the `BASE_URL` in `api_client.py`:

```python
BASE_URL = "http://your-backend-url:8000"
```

### Request Timeout
Adjust the timeout for API requests (default: 10 seconds):

```python
REQUEST_TIMEOUT = 10  # in seconds
```

## Customization

### Add New Features
1. Create a new method in `APIClient` class in `api_client.py`
2. Add a new section in `app.py` to display the data

### Styling
Custom CSS is embedded in `app.py`. Modify the `st.markdown()` call with custom CSS to change colors, fonts, or layout.

### Status Indicators
Status colors and indicators can be customized in the `get_status_indicator()` function.

## Troubleshooting

### "Failed to fetch data" Error
- Ensure the FastAPI backend is running on `http://127.0.0.1:8000`
- Check if the API is accessible: visit `http://127.0.0.1:8000/health` in your browser

### "Connection refused" Error
- Make sure the backend server is running
- Verify the `BASE_URL` is correct in `api_client.py`

### Timeout Errors
- Increase the `REQUEST_TIMEOUT` value in `api_client.py`
- Check backend performance and network connectivity

## Dependencies

- **streamlit**: Web app framework
- **requests**: HTTP client library
- **pandas**: Data manipulation (imported for future use)

## Notes

- No authentication required (as per requirements)
- No database used (stateless frontend)
- No WebSocket connections (simple HTTP polling)
- Frontend is read-only (no data modification)

## Support

For issues or questions:
1. Check the backend is running properly
2. Verify all API endpoints are accessible
3. Review the error messages in the Streamlit interface
4. Check the browser console for JavaScript errors

---

**Status**: Production Ready ✅
**Last Updated**: December 2024
