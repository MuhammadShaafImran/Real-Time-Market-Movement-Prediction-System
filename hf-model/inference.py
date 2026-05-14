import torch
import joblib
import numpy as np

from model_architecture import LSTMModel


INPUT_SIZE = 17
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.2


model = LSTMModel(
    input_size=INPUT_SIZE,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT
)

model.load_state_dict(
    torch.load("model.pth", map_location="cpu")
)

model.eval()

scaler = joblib.load("scaler.pkl")


def predict(data):

    features = np.array(
        data["inputs"],
        dtype=np.float32
    )

    scaled = scaler.transform(features)

    tensor = torch.FloatTensor(
        scaled
    ).unsqueeze(0)

    with torch.no_grad():

        outputs = model(tensor)

        probs = torch.softmax(
            outputs,
            dim=1
        )

        conf, pred = torch.max(
            probs,
            dim=1
        )

    return {
        "prediction": int(pred.item()),
        "confidence": float(conf.item())
    }