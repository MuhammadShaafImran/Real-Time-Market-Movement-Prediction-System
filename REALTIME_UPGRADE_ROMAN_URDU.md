# Real-Time Market Movement Prediction System
## Complete Roman Urdu Documentation

Yeh file project ka single canonical Roman Urdu reference hai. Is mein folder-wise working, file-wise role, pipeline flow, API endpoints, frontend behavior, Airflow orchestration, aur Docker URLs sab clearly explain kiye gaye hain.

## 1) Project Ka Overall Flow

Simple flow yeh hai:

Yahoo Finance + Reddit + Finnhub + Alpha Vantage
→ Airflow scheduled pipeline
→ `src/main.py`
→ ingestion + sentiment + feature engineering
→ processed parquet dataset
→ FastAPI backend
→ Streamlit frontend
→ live charts + live prediction

### Core idea

- Data manual refresh se nahi, schedule se chalti hai.
- Airflow har fixed interval par naya data aur naya dataset banata hai.
- Backend har request par fresh parquet read karta hai.
- Frontend auto-refresh karke latest API response dikhata hai.
- Training pipeline realtime ingestion se alag rakhi gayi hai.

## 2) Current Runtime Kahan Kya Chal Raha Hai

### Docker mode mein URLs

- Backend API: `http://localhost:8000`
- Frontend dashboard: `http://localhost:8501`
- Apache Airflow web UI: `http://localhost:8080`
- Postgres: `localhost:5432` par map hai, lekin usually direct use nahi hota

### Container-to-container communication

- Frontend container backend ko `http://backend:8000` se call karta hai.
- Airflow containers shared volume se `src/data` read/write karte hain.
- Backend aur Airflow dono same `src/data` volume dekhte hain, is liye latest parquet sab ko visible hoti hai.

## 3) Folder Wise Breakdown

### `api/`

Ye serving layer hai. Is ka kaam model inference, metadata endpoints, aur latest dataset read karna hai.

#### `api/app.py`

- FastAPI app yahan define hota hai.
- `load_dataset()` har request par latest parquet file read karta hai.
- Dataset memory mein permanently cache nahi hota.
- Predictive aur dashboard endpoints yahin expose hote hain.

#### `api/predictor.py`

- `lstm_state_dict.pth` load karta hai.
- `scaler.pkl` load karta hai.
- Input shape validate karta hai.
- 30 timesteps aur 17 features par inference chalata hai.
- Prediction, confidence, raw probabilities, aur signal strength return karta hai.

#### `api/schemas.py`

- `PredictionRequest` request payload define karta hai.
- `PredictionResponse` response shape define karta hai.
- `/predict` endpoint ka contract isi file se control hota hai.

#### `api/convert_model.py`

- Model conversion utility hai.
- Old format se clean `state_dict` banana ho to use hoti hai.

#### `api/download_model.py`

- Registered model ko download karne ke kaam aati hai.
- Model artifacts ko `models/` folder mein store karti hai.

### `frontend/`

Ye dashboard layer hai. Is ka kaam backend se live data lena aur Streamlit UI render karna hai.

#### `frontend/app.py`

- Streamlit dashboard define karta hai.
- Auto-refresh 30 seconds par hota hai.
- Top status metrics show hotay hain.
- Live ticker strip render hoti hai.
- Live prediction tab selected symbol par inference chalata hai.
- Price aur sentiment charts render hotay hain.
- Debug tab data availability check karta hai.

#### `frontend/api_client.py`

- Backend ke saath communication wrappers rakhta hai.
- Current frontend is endpoints ko use karta hai:
  - `/health`
  - `/model-info`
  - `/metrics`
  - `/dataset-info`
  - `/pipeline-status`
  - `/latest-update`
  - `/market-stream`
  - `/prediction-history/{symbol}`
  - `/pipeline-health`
  - `/available-symbols`
  - `/market-overview`
  - `/price-history/{symbol}`
  - `/sentiment-history/{symbol}`
  - `/predict-live/{symbol}`
  - `/debug-symbols`
- Note: `get_labels()` wrapper file mein maujood hai, lekin current backend `api/app.py` mein `/labels` endpoint nazar nahi aata. Is liye isay stale wrapper samjho.

#### `frontend/Dockerfile`

- Streamlit container build karta hai.
- Container ke andar `streamlit run app.py` chalata hai.

#### `frontend/requirements.txt`

- Streamlit dependencies rakhta hai.
- `streamlit-autorefresh` yahin se aata hai.

### `src/`

Ye actual data pipeline aur dataset building area hai.

#### `src/main.py`

Ye pipeline ka main entrypoint hai.

Flow normally yeh hota hai:

1. Yahoo Finance se price data aata hai.
2. Finnhub se news data aata hai.
3. Alpha Vantage se sentiment signals aate hain.
4. Reddit RSS se community sentiment aata hai.
5. Technical indicators calculate hotay hain.
6. Sentiment scores aggregate hotay hain.
7. Sab data merge hota hai.
8. Final ML dataset banta hai.
9. Latest parquet file save hoti hai.

#### `src/ingestion/yahoo_ingest.py`

- Market price candles fetch karta hai.
- Historical OHLCV data handle karta hai.

#### `src/ingestion/finnhub_ingest.py`

- Company news aur market news fetch karta hai.
- News headlines aur summaries lata hai.

#### `src/ingestion/alpha_vantage_ingest.py`

- `NEWS_SENTIMENT` type data use karta hai.
- Ticker-level sentiment scores nikalta hai.

#### `src/ingestion/reddit_rss_ingest.py`

- Reddit financial communities se posts lata hai.
- Market hype aur discussion signals build karne mein use hota hai.

#### `src/processing/feature_engineering.py`

- RSI
- MACD
- MACD signal
- SMA 20
- EMA 20
- Bollinger Bands

Ye technical indicators calculate hotay hain.

#### `src/processing/sentiment.py`

- Text sentiment analysis handle karta hai.
- FinBERT/VADER style analysis ka role yahan hota hai.

#### `src/processing/aggregate.py`

- Symbol wise sentiment aggregate karta hai.
- Time bucket ke hisaab se data align karta hai.

#### `src/dataset_generator/dataset_builder.py`

- Price data + sentiment data + Reddit data merge karta hai.
- Final ML label banata hai:
  - `1` = next close upar gaya
  - `0` = next close neeche gaya

### `Training/`

Ye training zone hai. Is ka kaam model ko retrain karna aur artifacts save karna hai.

#### `Training/run_training.py`

- Dataset load karta hai.
- Preprocess karta hai.
- Train/validation/test split karta hai.
- Scaler save karta hai.
- Models train karta hai.
- Output artifacts save karta hai.

#### `Training/trainer.py`

- PyTorch training loop chalata hai.
- Best model save karta hai.
- Test metrics calculate karta hai.

#### `Training/models.py`

- `RNNModel`
- `GRUModel`
- `LSTMModel`

#### `Training/config.py`

- Sequence length
- Hidden size
- Num layers
- Dropout
- Batch size
- Epochs
- Learning rate

### `airflow/`

Ye orchestration layer hai. Yahan scheduled jobs run hotay hain.

#### `airflow/dags/market_pipeline.py`

- Realtime ingestion DAG hai.
- Schedule: har 5 minute.
- Task order:
  - data ingestion
  - sentiment analysis
  - feature engineering
  - dataset generation
- Is DAG mein training nahi chalti.

#### `airflow/dags/model_training_pipeline.py`

- Separate daily training DAG hai.
- Model retraining ko realtime pipeline se alag rakhta hai.
- Task `python -m Training.run_training` chalata hai.

#### `airflow/Dockerfile`

- Custom Airflow image build karta hai.
- Project ki dependencies install karta hai.
- Is se Airflow ke andar project scripts properly chal sakte hain.

#### `airflow/requirements.txt`

- Airflow pipeline ke liye required packages rakhta hai.

#### `airflow/docker/docker-compose.yml`

- Purana compose setup hai.
- Current canonical entrypoint root wala `docker-compose.yml` hai.
- Agar confuse ho, root compose use karo.

### `models/`

Ye trained artifacts ka folder hai.

- `models/data/lstm_state_dict.pth`
- `models/data/model.pth`
- `models/data/scaler.pkl`
- `models/MLmodel`
- `models/conda.yaml`
- `models/python_env.yaml`
- `models/registered_model_meta`

### `README.md`

- Project ka short top-level intro aur Docker run steps rakhta hai.
- Long detailed explanation ke liye yeh Roman Urdu doc zyada complete hai.

## 4) API Endpoints Ka Complete Breakdown

### `GET /`

- Basic root check.
- Batata hai API run kar rahi hai ya nahi.

### `GET /health`

- API aur model status check karta hai.

### `GET /model-info`

- Model architecture details deta hai.
- Sequence length, hidden size, layers, dropout, optimizer, loss, epochs, batch size show karta hai.

### `GET /metrics`

- Test metrics deta hai:
  - accuracy
  - F1 score
  - RMSE
  - model comparison

### `GET /dataset-info`

- Total rows
- Total features
- Sequence length
- Symbols
- Data sources

### `GET /pipeline-status`

- High-level pipeline state deta hai.
- Ingestion, sentiment, feature engineering, model, aur API status show karta hai.

### `POST /predict`

- Direct inference endpoint hai.
- Input: 30 x 17 feature sequence.
- Output: prediction, confidence, model.

### `GET /latest-update`

- Latest dataset timestamp deta hai.
- File modify time deta hai.
- Latest symbol aur total rows/symbols deta hai.

### `GET /market-stream`

- Sab symbols ka live snapshot deta hai.
- Top bullish aur bearish symbols alag list mein deta hai.

### `GET /prediction-history/{symbol}`

- Selected symbol ki rolling prediction history deta hai.
- Last 20 records return hotay hain.

### `GET /pipeline-health`

- Airflow-managed dataset freshness aur pipeline health deta hai.

### `GET /available-symbols`

- Dataset mein available trading symbols ki list deta hai.

### `GET /debug-symbols`

- Debug endpoint hai.
- Symbols count, available features, missing features, aur per-symbol row counts deta hai.

### `GET /market-overview`

- Top symbols ka latest market snapshot deta hai.
- Price aur bullish/bearish signal show karta hai.

### `GET /price-history/{symbol}`

- Selected symbol ki last 30 price points deta hai.

### `GET /sentiment-history/{symbol}`

- Selected symbol ka sentiment trend deta hai.

### `GET /predict-live/{symbol}`

- Selected symbol ki latest 30 rows par live LSTM prediction karta hai.
- Prediction, confidence, probabilities, price, timestamp, aur signal strength deta hai.

## 5) Frontend Kaise Kaam Karta Hai

### `frontend/app.py` ka flow

1. Page load hota hai.
2. `st_autorefresh` 30 seconds par rerun karwata hai.
3. API se latest update, pipeline health, aur market stream aata hai.
4. Sidebar mein system status render hota hai.
5. Dashboard top metrics update hotay hain.
6. Live ticker strip latest symbols dikhati hai.
7. Predictions tab selected symbol par live inference chalata hai.
8. Price and sentiment tab charts banata hai.
9. Debug tab missing data aur symbol readiness dikhata hai.

### UI ka major idea

- User ko manual refresh button use nahi karna padta.
- Dashboard khud refresh hota rehta hai.
- Prediction tab, chart tab, aur debug tab alag alag perspective dete hain.

## 6) Backend Prediction Flow

Prediction ka exact flow yeh hai:

1. Request aati hai, ya to `/predict` se ya `/predict-live/{symbol}` se.
2. Backend latest parquet read karta hai.
3. Selected symbol ki last 30 rows uthata hai.
4. 17 feature columns correct order mein select hoti hain.
5. `scaler.pkl` se values scale hoti hain.
6. LSTM model inference karta hai.
7. Softmax se probabilities nikalti hain.
8. Confidence aur class label return hota hai.
9. Live endpoint mein `signal_strength` bhi add hoti hai.

### Signal strength logic

- `prob_up >= 0.75` ho to `STRONG_BULLISH`
- `prob_down >= 0.75` ho to `STRONG_BEARISH`
- `prob_up >= prob_down` ho to `BULLISH`
- warna `BEARISH`

## 7) Airflow Pipeline Kaise Work Kar Rahi Hai

### Realtime pipeline: `real_time_market_pipeline`

Schedule: har 5 minute

Task order:

1. `data_ingestion`
2. `sentiment_analysis`
3. `feature_engineering`
4. `dataset_generation`

#### Har task ka role

- `data_ingestion`: source data laata hai.
- `sentiment_analysis`: text/news sentiment nikalta hai.
- `feature_engineering`: RSI, MACD, EMA, SMA, Bollinger jaise features banata hai.
- `dataset_generation`: final ML-ready parquet build karta hai.

### Training pipeline: `market_model_training_pipeline`

Schedule: daily

- Ye model retraining ke liye hai.
- Realtime pipeline se separate hai.
- Iska purpose model ko periodically update karna hai, na ke har 5 minute retrain karna.

## 8) Docker Setup Ka Simple Meaning

Root `docker-compose.yml` ab sab ko ek saath manage karta hai:

- `postgres`: Airflow database ke liye
- `airflow-init`: DB migrate aur admin user create karta hai
- `airflow-webserver`: Airflow UI chalata hai
- `airflow-scheduler`: DAGs schedule karta hai
- `backend`: FastAPI API chalata hai
- `frontend`: Streamlit dashboard chalata hai

### Shared data volume

- `./src/data` Airflow aur backend dono mein mount hota hai.
- Is se Airflow jo latest dataset banata hai, backend usi ko read karta hai.
- Isi wajah se frontend ko fresh data milta rehta hai.

## 9) Run Kaise Karna Hai

### Sirf Docker se chalana

```powershell
docker compose up --build
```

### Open karne wali URLs

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:8501`
- Airflow: `http://localhost:8080`

### Airflow default login

- Username: `admin`
- Password: `admin`

## 10) Local Non-Docker Run Ka High-Level Idea

Agar Docker ke baghair run karna ho to flow yeh hota hai:

1. Python environment banaao.
2. Dependencies install karo.
3. `src/main.py` run karke dataset update karo.
4. `uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload`
5. `streamlit run app.py` inside `frontend/`
6. Airflow ko alag se setup karo, lekin Windows par Docker zyada practical hai.

## 11) Important Notes

- Backend serving-only design par hai.
- Model startup par load hota hai.
- Dataset har request par fresh read hoti hai.
- Frontend auto-refresh karta hai.
- Realtime pipeline aur training pipeline separate rakhi gayi hain.
- Old manual refresh style ab project ka main flow nahi hai.
- Current frontend client mein kuch purane wrappers ho sakte hain, is liye documentation mein backend endpoints ko source of truth samjho.

## 12) Sab Se Important Files Ek Nazar Mein

- [docker-compose.yml](docker-compose.yml)
- [api/app.py](api/app.py)
- [api/predictor.py](api/predictor.py)
- [api/schemas.py](api/schemas.py)
- [frontend/app.py](frontend/app.py)
- [frontend/api_client.py](frontend/api_client.py)
- [airflow/dags/market_pipeline.py](airflow/dags/market_pipeline.py)
- [airflow/dags/model_training_pipeline.py](airflow/dags/model_training_pipeline.py)
- [Training/run_training.py](Training/run_training.py)
- [src/main.py](src/main.py)

## 13) Short Final Summary

Is project mein Airflow data pipeline chalaata hai, FastAPI latest dataset par inference deta hai, aur Streamlit dashboard live view show karta hai. Docker mode mein sab kuch ek hi compose se run hota hai: backend, frontend, Airflow, aur Postgres. Backend aur Airflow same shared `src/data` volume use karte hain, is liye system near real-time feel deta hai.

Agar chaho to next step mein main is documentation ka short English version ya README ke andar direct link bhi add kar sakta hoon.
