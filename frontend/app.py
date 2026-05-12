"""
Real-Time Market Movement Prediction System - Streamlit Frontend
Professional dashboard for ML-based financial market prediction
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from api_client import get_api_client


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Market Movement Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .status-active {
        color: #09ab3b;
        font-weight: bold;
    }
    .status-inactive {
        color: #ff4b4b;
        font-weight: bold;
    }
    .market-signal-bullish {
        color: #09ab3b;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .market-signal-bearish {
        color: #ff4b4b;
        font-weight: bold;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_status_indicator(status: str) -> str:
    """Get status indicator emoji"""
    status_lower = status.lower()
    if status_lower in ["active", "running", "online", "ok"]:
        return "🟢"
    elif status_lower in ["inactive", "offline", "error"]:
        return "🔴"
    else:
        return "🟡"


def format_metric(value: float, decimals: int = 3) -> str:
    """Format metric value"""
    return f"{value:.{decimals}f}"


def display_error(message: str):
    """Display error message"""
    st.error(f"❌ {message}")


def display_success(message: str):
    """Display success message"""
    st.success(f"✅ {message}")


# ============================================================
# SIDEBAR - STATUS INFORMATION
# ============================================================

st.sidebar.markdown("## 📊 System Status")
st.sidebar.divider()

api_client = get_api_client()

# API Status
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### API")
    
    try:
        health = api_client.health_check()
        if "status" not in health or health.get("status") == "error":
            with col2:
                st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)
        else:
            api_status = health.get("api", "unknown").upper()
            with col2:
                st.markdown(f'<span class="status-active">{get_status_indicator(api_status)} Online</span>', unsafe_allow_html=True)
    except:
        with col2:
            st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)

    st.divider()

    # Model Status
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### Model")
    
    try:
        model_info = api_client.get_model_info()
        if "status" not in model_info or model_info.get("status") == "error":
            with col2:
                st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)
        else:
            model_name = model_info.get("model_name", "Unknown")
            with col2:
                st.markdown(f'<span class="status-active">🟢 {model_name}</span>', unsafe_allow_html=True)
    except:
        with col2:
            st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)

    st.divider()

    # Pipeline Status
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("### Pipeline")
    
    try:
        pipeline = api_client.get_pipeline_status()
        if "status" not in pipeline or pipeline.get("status") == "error":
            with col2:
                st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)
        else:
            model_status = pipeline.get("model_status", "unknown").upper()
            with col2:
                st.markdown(f'<span class="status-active">{get_status_indicator(model_status)} {model_status}</span>', unsafe_allow_html=True)
    except:
        with col2:
            st.markdown('<span class="status-inactive">🔴 Offline</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("*Last updated: Just now*")


# ============================================================
# MAIN CONTENT - HEADER
# ============================================================

col1, col2 = st.columns([1, 5])

with col1:
    st.markdown("## 📈")

with col2:
    st.markdown("## Real-Time Market Movement Prediction System")
    st.markdown("*LSTM-based financial market prediction using multi-source data fusion*")

st.divider()


# ============================================================
# METRICS SECTION
# ============================================================

st.markdown("### 📊 Model Performance Metrics")

try:
    metrics = api_client.get_metrics()
    
    if metrics.get("status") == "error":
        display_error(metrics.get("message", "Failed to fetch metrics"))
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            accuracy = metrics.get("final_test_accuracy", 0)
            st.metric(
                "Test Accuracy",
                f"{format_metric(accuracy, 3)}",
                delta=None,
                help="Classification accuracy on test set"
            )
        
        with col2:
            f1_score = metrics.get("final_test_f1_score", 0)
            st.metric(
                "F1 Score",
                f"{format_metric(f1_score, 3)}",
                delta=None,
                help="Harmonic mean of precision and recall"
            )
        
        with col3:
            rmse = metrics.get("final_test_rmse", 0)
            st.metric(
                "RMSE",
                f"{format_metric(rmse, 3)}",
                delta=None,
                help="Root Mean Squared Error"
            )
except Exception as e:
    display_error(f"Error loading metrics: {str(e)}")

st.divider()


# ============================================================
# LATEST MARKET SNAPSHOT SECTION
# ============================================================

st.markdown("### 💹 Latest Market Snapshot")

try:
    market_data = api_client.get_latest_market_data()
    
    if market_data.get("status") == "error":
        display_error(market_data.get("message", "Failed to fetch market data"))
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            symbol = market_data.get("symbol", "N/A")
            st.metric("Symbol", symbol, help="Trading symbol")
        
        with col2:
            timestamp = market_data.get("timestamp", "N/A")
            st.metric("Timestamp", timestamp[:10] if isinstance(timestamp, str) else timestamp)
        
        with col3:
            close_price = market_data.get("close_price", 0)
            st.metric("Close Price", f"${close_price:.2f}", help="Last closing price")
        
        with col4:
            market_signal = market_data.get("market_signal", "NEUTRAL")
            signal_color = "🟢" if market_signal == "Bullish" else "🔴"
            st.metric("Market Signal", f"{signal_color} {market_signal}")
        
        # Technical Indicators
        st.markdown("**Technical Indicators**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            rsi = market_data.get("RSI", 0)
            st.metric("RSI (14)", f"{format_metric(rsi, 2)}", help="Relative Strength Index")
        
        with col2:
            macd = market_data.get("MACD", 0)
            st.metric("MACD", f"{format_metric(macd, 4)}", help="MACD value")
        
        with col3:
            reddit_hype = market_data.get("reddit_hype", 0)
            st.metric("Reddit Hype", f"{format_metric(reddit_hype, 3)}", help="Reddit sentiment score")
        
        with col4:
            news_count = market_data.get("news_count", 0)
            st.metric("News Count", int(news_count), help="Number of news items")
        
        # Market Sentiment
        st.markdown("**Sentiment Analysis**")
        col1, col2 = st.columns(2)
        
        with col1:
            market_sentiment = market_data.get("market_sentiment", 0)
            st.metric("Market Sentiment Score", f"{format_metric(market_sentiment, 3)}", 
                     help="Overall market sentiment (-1 to 1)")

except Exception as e:
    display_error(f"Error loading market data: {str(e)}")

st.divider()


# ============================================================
# DATASET INFORMATION SECTION
# ============================================================

st.markdown("### 📁 Dataset Information")

try:
    dataset_info = api_client.get_dataset_info()
    
    if dataset_info.get("status") == "error":
        display_error(dataset_info.get("message", "Failed to fetch dataset info"))
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_rows = dataset_info.get("total_rows", 0)
            st.metric("Total Rows", f"{int(total_rows):,}")
        
        with col2:
            total_features = dataset_info.get("total_features", 0)
            st.metric("Total Features", int(total_features))
        
        with col3:
            seq_length = dataset_info.get("sequence_length", 0)
            st.metric("Sequence Length", int(seq_length))
        
        # Market Symbols
        st.markdown("**Market Symbols**")
        symbols = dataset_info.get("market_symbols", [])
        if symbols:
            symbols_str = ", ".join(str(s) for s in symbols[:10])
            if len(symbols) > 10:
                symbols_str += f", ... and {len(symbols) - 10} more"
            st.caption(symbols_str)
        else:
            st.caption("No symbols available")
        
        # Data Sources
        st.markdown("**Data Sources**")
        sources = dataset_info.get("data_sources", [])
        source_cols = st.columns(len(sources))
        for idx, source in enumerate(sources):
            with source_cols[idx]:
                st.info(f"✓ {source}")

except Exception as e:
    display_error(f"Error loading dataset info: {str(e)}")

st.divider()


# ============================================================
# PREDICTION SECTION
# ============================================================

st.markdown("### 🔮 Make a Prediction")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("Click the button below to generate a prediction using sample market data.")

with col2:
    predict_button = st.button(
        "🎯 Generate Prediction",
        key="predict_btn",
        use_container_width=True
    )

if predict_button:
    with st.spinner("Fetching sample input and generating prediction..."):
        try:
            # Fetch sample input
            sample_input = api_client.get_sample_input()
            
            if sample_input.get("status") == "error":
                display_error(f"Failed to fetch sample input: {sample_input.get('message')}")
            else:
                features = sample_input.get("features", [])
                
                # Make prediction
                prediction_result = api_client.predict(features)
                
                if prediction_result.get("status") == "error":
                    display_error(f"Prediction failed: {prediction_result.get('message')}")
                else:
                    st.divider()
                    st.markdown("### 📊 Prediction Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    prediction = prediction_result.get("prediction", "N/A")
                    confidence = prediction_result.get("confidence", 0)
                    model_name = prediction_result.get("model", "Unknown")
                    
                    with col1:
                        pred_emoji = "🟢" if prediction == "UP" else "🔴"
                        st.metric(
                            "Prediction",
                            f"{pred_emoji} {prediction}",
                            help="Market movement direction"
                        )
                    
                    with col2:
                        st.metric(
                            "Confidence Score",
                            f"{format_metric(confidence, 3)}",
                            help="Model confidence in this prediction"
                        )
                    
                    with col3:
                        st.metric(
                            "Model Used",
                            model_name,
                            help="Model architecture version"
                        )
                    
                    display_success("Prediction generated successfully!")
                    
        except Exception as e:
            display_error(f"An error occurred: {str(e)}")

st.divider()


# ============================================================
# MODEL INFORMATION SECTION
# ============================================================

st.markdown("### 🧠 Model Architecture")

try:
    model_info = api_client.get_model_info()
    
    if model_info.get("status") == "error":
        display_error(model_info.get("message", "Failed to fetch model info"))
    else:
        # Create a clean layout for model specs
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Configuration**")
            st.write(f"**Model Name:** {model_info.get('model_name', 'N/A')}")
            st.write(f"**Architecture:** {model_info.get('architecture', 'N/A')}")
            st.write(f"**Sequence Length:** {model_info.get('sequence_length', 'N/A')}")
            st.write(f"**Input Size:** {model_info.get('input_size', 'N/A')} features")
        
        with col2:
            st.markdown("**Training Configuration**")
            st.write(f"**Hidden Size:** {model_info.get('hidden_size', 'N/A')}")
            st.write(f"**Number of Layers:** {model_info.get('num_layers', 'N/A')}")
            st.write(f"**Dropout Rate:** {model_info.get('dropout', 'N/A')}")
            st.write(f"**Optimizer:** {model_info.get('optimizer', 'N/A')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Training Details**")
            st.write(f"**Loss Function:** {model_info.get('loss_function', 'N/A')}")
            st.write(f"**Epochs:** {model_info.get('epochs', 'N/A')}")
        
        with col2:
            st.markdown("**Inference Details**")
            st.write(f"**Batch Size:** {model_info.get('batch_size', 'N/A')}")

except Exception as e:
    display_error(f"Error loading model info: {str(e)}")

st.divider()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85rem;'>
    <p>Real-Time Market Movement Prediction System | LSTM-based Financial AI</p>
    <p>Backend: FastAPI | Frontend: Streamlit | Data Sources: Yahoo Finance, Reddit, Finnhub, Alpha Vantage</p>
    </div>
    """, unsafe_allow_html=True)
