# api/predictor.py

from pathlib import Path
import numpy as np
import torch
import joblib

from Training.models import LSTMModel


# ============================================================
# CONFIG
# ============================================================

INPUT_SIZE = 17
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.2
SEQ_LENGTH = 30

CLASS_MAPPING = {
    0: "DOWN",
    1: "UP"
}


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    ROOT_DIR
    / "models"
    / "data"
    / "lstm_state_dict.pth"
)

SCALER_PATH = (
    ROOT_DIR
    / "models"
    / "data"
    / "scaler.pkl"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD SCALER
# ============================================================

print("Loading scaler...")

scaler = joblib.load(SCALER_PATH)

print("Scaler loaded successfully.")


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading LSTM model...")

model = LSTMModel(
    input_size=INPUT_SIZE,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT
)

state_dict = torch.load(
    MODEL_PATH,
    map_location=DEVICE
)

model.load_state_dict(state_dict)

model.to(DEVICE)

model.eval()

print("LSTM model loaded successfully.")


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict(features):
    """
    Input:
        30 x 17 sequence

    Output:
        prediction + confidence
    """

    # ========================================================
    # VALIDATE INPUT SHAPE
    # ========================================================

    if len(features) != SEQ_LENGTH:
        raise ValueError(
            f"Expected {SEQ_LENGTH} timesteps, got {len(features)}"
        )

    for row in features:

        if len(row) != INPUT_SIZE:
            raise ValueError(
                f"Each timestep must contain {INPUT_SIZE} features"
            )

    # ========================================================
    # CONVERT TO NUMPY
    # ========================================================

    features_np = np.array(
        features,
        dtype=np.float32
    )

    # Shape:
    # (30, 17)

    # ========================================================
    # SCALE FEATURES
    # ========================================================

    scaled_features = scaler.transform(features_np)

    # ========================================================
    # CONVERT TO TENSOR
    # ========================================================

    input_tensor = torch.FloatTensor(
        scaled_features
    )

    # Add batch dimension:
    # (30,17) -> (1,30,17)

    input_tensor = input_tensor.unsqueeze(0)

    input_tensor = input_tensor.to(DEVICE)

    # ========================================================
    # MODEL INFERENCE
    # ========================================================

    with torch.no_grad():

        outputs = model(input_tensor)

        probabilities = torch.softmax(
            outputs,
            dim=1
        )

        confidence, predicted_class = torch.max(
            probabilities,
            dim=1
        )

    # ========================================================
    # FORMAT OUTPUT
    # ========================================================

    predicted_index = predicted_class.item()

    prediction_label = CLASS_MAPPING[predicted_index]

    confidence_score = round(
        confidence.item(),
        4
    )

    return {
        "prediction": prediction_label,
        "confidence": confidence_score,
        "model": "LSTM_Best"
    }