Training package
===============

This folder contains scripts ported from `src/notebooks/Train.ipynb` to run training from the command line or inside Docker.

Quick start
-----------

Run locally (from repository root):

```bash
python Training/run_training.py --dataset src/data/processed/latest_ml_dataset_v4_finbert.parquet
```

Train only specific models:

```bash
python Training/run_training.py --models rnn,lstm
```

Build Docker image:

```bash
docker build -t rtm-train -f Training/Dockerfile .
docker run --rm rtm-train
```

Files
-----
- `config.py` - hyperparameters and defaults
- `data.py` - data loading, preprocessing and sequence creation
- `models.py` - RNN/GRU/LSTM model classes
- `trainer.py` - training loop and evaluation
- `run_training.py` - CLI entrypoint
