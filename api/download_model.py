from pathlib import Path
import mlflow
import dagshub

REPO_OWNER = "shaafimran257"
REPO_NAME = "Real-Time-Market-Movement-Prediction-System"

REGISTERED_MODEL_NAME = "LSTM_Best"

# ROOT PROJECT PATH
ROOT_DIR = Path(__file__).resolve().parent.parent

# MODELS FOLDER
MODELS_DIR = ROOT_DIR / "models"

dagshub.init(
    repo_owner=REPO_OWNER,
    repo_name=REPO_NAME,
    mlflow=True
)

print(f"Connecting to DagsHub to fetch '{REGISTERED_MODEL_NAME}'...")

try:
    local_path = mlflow.artifacts.download_artifacts(
        artifact_uri=f"models:/{REGISTERED_MODEL_NAME}/latest",
        dst_path=str(MODELS_DIR)
    )

    print("✅ Success! Model downloaded successfully.")
    print(f"📁 Model saved at: {local_path}")

except Exception as e:
    print(f"❌ Error downloading model: {e}")