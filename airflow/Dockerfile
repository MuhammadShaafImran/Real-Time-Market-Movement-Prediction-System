FROM apache/airflow:2.8.1

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY airflow/requirements.txt /requirements-airflow.txt

USER airflow

RUN pip install --no-cache-dir -r /requirements-airflow.txt

WORKDIR /opt/project
