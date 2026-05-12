import torch.nn as nn


class RNNModel(nn.Module):
    """Simple RNN model for classification"""
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super(RNNModel, self).__init__()
        self.rnn = nn.RNN(input_size, hidden_size, num_layers,
                          batch_first=True, dropout=dropout)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        _, h_n = self.rnn(x)
        out = self.classifier(h_n[-1])
        return out


class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super(GRUModel, self).__init__()
        self.gru = nn.GRU(input_size, hidden_size, num_layers,
                          batch_first=True, dropout=dropout)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        _, h_n = self.gru(x)
        out = self.classifier(h_n[-1])
        return out


class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=dropout)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        _, (h_n, _) = self.lstm(x)
        out = self.classifier(h_n[-1])
        return out
