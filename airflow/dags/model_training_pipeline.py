from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {
    "owner": "market-ai",
    "depends_on_past": False,
    "start_date": datetime(2026, 5, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


dag = DAG(
    dag_id="market_model_training_pipeline",
    default_args=default_args,
    description="Scheduled model retraining pipeline",
    schedule="@daily",
    catchup=False,
)

model_training = BashOperator(
    task_id="model_training",
    bash_command="cd /opt/project && python -m Training.run_training",
    dag=dag,
)
