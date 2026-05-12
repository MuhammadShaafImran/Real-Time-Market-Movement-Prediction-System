from pathlib import Path
import torch


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

OLD_MODEL_PATH = ROOT_DIR / "models" / "data" / "model.pth"

NEW_MODEL_PATH = ROOT_DIR / "models" / "data" / "lstm_state_dict.pth"


# ============================================================
# LOAD OLD MODEL
# ============================================================

print("Loading original MLflow model...")

model = torch.load(
    OLD_MODEL_PATH,
    weights_only=False,
    map_location="cpu"
)

print("Model loaded successfully.")


# ============================================================
# SAVE CLEAN STATE_DICT
# ============================================================

torch.save(
    model.state_dict(),
    NEW_MODEL_PATH
)

print("Clean state_dict saved successfully.")

print(f"Saved at: {NEW_MODEL_PATH}")