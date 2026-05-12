from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


# ============================================================
# DEFAULT DAG CONFIG
# ============================================================

default_args = {
    "owner": "market-ai",
    "depends_on_past": False,
    "start_date": datetime(2026, 5, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


# ============================================================
# DAG DEFINITION
# ============================================================

dag = DAG(
    dag_id="real_time_market_pipeline",
    default_args=default_args,
    description="Market Movement Prediction Pipeline",
    schedule="@daily",
    catchup=False,
)


# ============================================================
# TASK 1 — DATA INGESTION
# ============================================================

data_ingestion = BashOperator(
    task_id="data_ingestion",
    bash_command="cd /opt/project && python src/main.py",
    dag=dag,
)


# ============================================================
# TASK 2 — SENTIMENT ANALYSIS
# ============================================================

sentiment_analysis = BashOperator(
    task_id="sentiment_analysis",
    bash_command='echo "Running FinBERT sentiment analysis..."',
    dag=dag,
)


# ============================================================
# TASK 3 — FEATURE ENGINEERING
# ============================================================

feature_engineering = BashOperator(
    task_id="feature_engineering",
    bash_command='echo "Computing RSI, MACD, EMA, SMA..."',
    dag=dag,
)


# ============================================================
# TASK 4 — DATASET GENERATION
# ============================================================

dataset_generation = BashOperator(
    task_id="dataset_generation",
    bash_command='echo "Generating ML dataset..."',
    dag=dag,
)


# ============================================================
# TASK 5 — MODEL TRAINING
# ============================================================

model_training = BashOperator(
    task_id="model_training",
    bash_command="cd /opt/project && python Training/run_training.py",
    dag=dag,
)


# ============================================================
# PIPELINE ORDER
# ============================================================

(
    data_ingestion
    >> sentiment_analysis
    >> feature_engineering
    >> dataset_generation
    >> model_training
)