"""Entrypoint to train models (RNN/GRU/LSTM) using code ported from Train.ipynb."""
import argparse
import json
from pathlib import Path
import mlflow

from . import config
from . import data as data_mod
from . import models
from . import trainer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default=str(config.DATASET_PATH))
    parser.add_argument('--models', type=str, default='rnn,gru,lstm', help='Comma-separated models to train')
    parser.add_argument('--mlflow_uri', type=str, default=None)
    parser.add_argument('--results_out', type=str, default='training_results.json')
    args = parser.parse_args()

    if args.mlflow_uri:
        mlflow.set_tracking_uri(args.mlflow_uri)

    dataset_path = Path(args.dataset)
    print(f"Loading dataset from: {dataset_path}")
    df = data_mod.load_parquet(dataset_path)
    X_df, y, label_encoder = data_mod.preprocess(df)

    (X_train, y_train, X_val, y_val, X_test, y_test) = data_mod.split_scale_and_tensorize(
        X_df, y, seq_length=config.SEQ_LENGTH)

    selected = [m.strip().lower() for m in args.models.split(',') if m.strip()]
    model_map = {
        'rnn': models.RNNModel,
        'gru': models.GRUModel,
        'lstm': models.LSTMModel
    }

    results = {}
    for key in selected:
        if key not in model_map:
            print(f"Unknown model key: {key}, skipping.")
            continue
        model_cls = model_map[key]
        print(f"Training {key.upper()}...")
        model_obj, best_val_acc, metrics = trainer.train_and_evaluate_model(
            model_cls, key.upper(), X_train, y_train, X_val, y_val, X_test, y_test
        )
        results[key.upper()] = metrics

    with open(args.results_out, 'w') as fh:
        json.dump(results, fh, indent=2)

    print(f"Training complete. Results written to {args.results_out}")


if __name__ == '__main__':
    main()
