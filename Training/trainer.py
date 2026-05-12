import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import confusion_matrix, f1_score
from . import config


def calculate_rmse(y_true, y_pred):
    mse = ((y_true - y_pred) ** 2).mean()
    return float(mse ** 0.5)


def train_and_evaluate_model(model_class, model_name,
                             X_train, y_train, X_val, y_val, X_test, y_test,
                             device=None):
    device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

    model = model_class(X_train.shape[2], config.HIDDEN_SIZE, config.NUM_LAYERS, config.DROPOUT)
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)

    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=config.BATCH_SIZE, shuffle=True)

    best_val_accuracy = 0
    best_model_state = None

    for epoch in range(config.EPOCHS):
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0

        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_correct += (predicted == y_batch).sum().item()
            train_total += y_batch.size(0)

        train_loss /= max(1, len(train_loader))
        train_accuracy = train_correct / max(1, train_total)

        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val.to(device))
            _, val_predicted = torch.max(val_outputs, 1)
            val_correct = (val_predicted == y_val.to(device)).sum().item()
            val_accuracy = val_correct / len(y_val)

        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            best_model_state = model.state_dict().copy()

        if (epoch + 1) % 5 == 0:
            print(f"[{model_name}] Epoch {epoch+1}/{config.EPOCHS} | Train Acc: {train_accuracy:.4f} | Val Acc: {val_accuracy:.4f}")

    # Load best and test
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test.to(device))
        _, test_predicted = torch.max(test_outputs, 1)

        y_true_np = y_test.cpu().numpy()
        y_pred_np = test_predicted.cpu().numpy()

        test_accuracy = (test_predicted == y_test.to(device)).sum().item() / len(y_test)
        test_f1 = f1_score(y_true_np, y_pred_np, average='weighted')
        test_rmse = calculate_rmse(y_true_np, y_pred_np)
        cm = confusion_matrix(y_true_np, y_pred_np)

    # Save confusion matrix artifact
    cm_path = f"{model_name}_cm.png"
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title(f'CM: {model_name}')
    plt.ylabel('True')
    plt.xlabel('Pred')
    plt.savefig(cm_path)
    plt.close()

    metrics = {
        'final_test_accuracy': float(test_accuracy),
        'final_test_f1_score': float(test_f1),
        'final_test_rmse': float(test_rmse),
        'confusion_matrix_image': cm_path
    }

    return model, best_val_accuracy, metrics
