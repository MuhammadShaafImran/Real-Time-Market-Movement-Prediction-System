FROM python:3.10-slim
WORKDIR /app

# Install system deps for pandas/torch as needed (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /app
CMD ["python", "Training/run_training.py"]
