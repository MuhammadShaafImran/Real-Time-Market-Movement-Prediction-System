"""Configuration and hyperparameters for training."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Dataset
DATASET_PATH = ROOT / "src" / "data" / "processed" / "latest_ml_dataset_v4_finbert.parquet"

# Sequence / model
SEQ_LENGTH = 30
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.2

# Training
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 1e-3

# Misc
DEVICE = None  # resolved at runtime
