import numpy as np
import torch
import torch.nn as nn


class LSTMModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        out, _ = self.lstm(x)       # (batch, seq, hidden)
        return self.head(out[:, -1, :])  # last timestep


class TCNBlock(nn.Module):
    def __init__(self, in_ch, out_ch, kernel_size, dilation, dropout):
        super().__init__()
        self.conv1 = nn.Conv1d(in_ch, out_ch, kernel_size, padding=(kernel_size - 1) * dilation, dilation=dilation)
        self.conv2 = nn.Conv1d(out_ch, out_ch, kernel_size, padding=(kernel_size - 1) * dilation, dilation=dilation)
        self.bn1 = nn.BatchNorm1d(out_ch)
        self.bn2 = nn.BatchNorm1d(out_ch)
        self.relu = nn.ReLU()
        self.drop = nn.Dropout(dropout)
        self.residual = nn.Conv1d(in_ch, out_ch, 1) if in_ch != out_ch else nn.Identity()

    def forward(self, x):
        res = self.residual(x)
        out = self.conv1(x)
        out = out[:, :, :x.size(2)]  # trim causal padding
        out = self.bn1(out)
        out = self.relu(out)
        out = self.drop(out)
        out = self.conv2(out)
        out = out[:, :, :x.size(2)]
        out = self.bn2(out)
        out = self.relu(out + res)
        return out


class TCNModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        channels = [hidden_size] * num_layers
        layers = []
        in_ch = input_size
        for i, out_ch in enumerate(channels):
            layers.append(TCNBlock(in_ch, out_ch, kernel_size=3, dilation=2**i, dropout=dropout))
            in_ch = out_ch
        self.tcn = nn.Sequential(*layers)
        self.head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.BatchNorm1d(hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.BatchNorm1d(hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, 1),
        )

    def forward(self, x):
        # x: (batch, seq, features) -> (batch, features, seq)
        out = self.tcn(x.permute(0, 2, 1))
        out = out[:, :, -1]  # last timestep
        return self.head(out)


class AttentionBlock(nn.Module):
    """Multi-head self-attention with residual connection."""
    def __init__(self, hidden_size: int, nhead: int = 8, dropout: float = 0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size,
            num_heads=nhead,
            dropout=dropout,
            batch_first=True,
        )
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        self.ffn = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size * 4, hidden_size),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        # Self-attention with residual
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + attn_out)
        # FFN with residual
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x


class AttentionTransformer(nn.Module):
    """Transformer with custom attention blocks for time series."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.hidden_size = hidden_size

        # Input projection
        self.input_projection = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
        )

        # Positional encoding
        self.pos_encoding = PositionalEncoding(hidden_size, dropout)

        # Stack of attention blocks
        nhead = min(8, hidden_size // 16)
        self.attention_blocks = nn.ModuleList([
            AttentionBlock(hidden_size, nhead, dropout)
            for _ in range(num_layers)
        ])

        # Output head
        self.head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1),
        )

    def forward(self, x):
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        for block in self.attention_blocks:
            x = block(x)
        x = x[:, -1, :]  # last timestep
        return self.head(x)


class TransformerModel(nn.Module):
    """Transformer with multi-head attention for time series."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.hidden_size = hidden_size

        # Input projection with layer norm
        self.input_projection = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
        )

        # Positional encoding
        self.pos_encoding = PositionalEncoding(hidden_size, dropout)

        # Transformer encoder with more heads for better attention
        nhead = min(8, hidden_size // 16)  # 8 heads for 128, 4 for 64
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=nhead,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            batch_first=True,
            activation='gelu',
            norm_first=True,  # Pre-norm for better training
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        # Output head
        self.head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.LayerNorm(hidden_size // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.LayerNorm(hidden_size // 4),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 4, 1),
        )

    def forward(self, x):
        # x: (batch, seq, features)
        x = self.input_projection(x)  # (batch, seq, hidden)
        x = self.pos_encoding(x)
        x = self.transformer(x)  # (batch, seq, hidden)
        x = x[:, -1, :]  # Take last timestep
        return self.head(x)


class PositionalEncoding(nn.Module):
    """Positional encoding for Transformer."""
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class LSTMRegression(nn.Module):
    """LSTM for regression - predicts price change magnitude."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),  # Predict price change %
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


class TCNRegression(nn.Module):
    """TCN for regression - predicts price change magnitude."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        channels = [hidden_size] * num_layers
        layers = []
        in_ch = input_size
        for i, out_ch in enumerate(channels):
            layers.append(TCNBlock(in_ch, out_ch, kernel_size=3, dilation=2**i, dropout=dropout))
            in_ch = out_ch
        self.tcn = nn.Sequential(*layers)
        self.head = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        out = self.tcn(x.permute(0, 2, 1))
        out = out[:, :, -1]
        return self.head(out)


class TransformerRegression(nn.Module):
    """Transformer for regression - predicts price change magnitude."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_projection = nn.Linear(input_size, hidden_size)
        self.pos_encoding = PositionalEncoding(hidden_size, dropout)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size,
            nhead=4,
            dim_feedforward=hidden_size * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.head = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        x = self.transformer(x)
        x = x[:, -1, :]
        return self.head(x)


class MultiTaskModel(nn.Module):
    """Multi-task model: classification + regression."""
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
        )
        # Classification head (buy/sell)
        self.class_head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )
        # Regression head (price change %)
        self.reg_head = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )
        # Confidence head (how confident in prediction)
        self.conf_head = nn.Sequential(
            nn.Linear(hidden_size, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),  # 0-1 confidence
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        features = out[:, -1, :]
        classification = self.class_head(features)
        regression = self.reg_head(features)
        confidence = self.conf_head(features)
        return classification, regression, confidence


def build_model(config, input_size: int) -> nn.Module:
    model_type = config.model_type.lower()

    if model_type == "tcn":
        return TCNModel(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "transformer":
        return TransformerModel(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "attention":
        return AttentionTransformer(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "lstm_reg":
        return LSTMRegression(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "tcn_reg":
        return TCNRegression(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "transformer_reg":
        return TransformerRegression(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "multi_task":
        return MultiTaskModel(input_size, config.hidden_size, config.num_layers, config.dropout)
    return LSTMModel(input_size, config.hidden_size, config.num_layers, config.dropout)


class Ensemble:
    """Ensemble of N models with optional weighted averaging."""

    def __init__(self, models: list, weights: list = None):
        self.models = models
        if weights is None:
            self.weights = [1.0 / len(models)] * len(models)
        else:
            total = sum(weights)
            self.weights = [w / total for w in weights]

    def eval(self):
        for m in self.models:
            m.eval()

    def __call__(self, x):
        """Weighted average of logits from all models."""
        logits = torch.stack([m(x) for m in self.models])  # (N, batch, 1)
        weights = torch.tensor(self.weights, device=x.device).view(-1, 1, 1)
        return (logits * weights).sum(dim=0)  # (batch, 1)

    def save(self, path):
        state = {
            "models": [{k: v.cpu() for k, v in m.state_dict().items()} for m in self.models],
            "weights": self.weights,
        }
        torch.save(state, path)

    @classmethod
    def load(cls, path, config, input_size, device="cpu"):
        data = torch.load(path, map_location=device, weights_only=True)
        if isinstance(data, dict):
            states = data["models"]
            weights = data.get("weights")
        else:
            states = data
            weights = None
        models = []
        for state in states:
            m = build_model(config, input_size)
            m.load_state_dict(state)
            m.to(device)
            models.append(m)
        return cls(models, weights)


class StackingEnsemble(nn.Module):
    """Stacking: meta-learner trained on base model predictions."""

    def __init__(self, base_models: list, meta_hidden: int = 16):
        super().__init__()
        self.base_models = nn.ModuleList(base_models)
        n_base = len(base_models)
        self.meta = nn.Sequential(
            nn.Linear(n_base, meta_hidden),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(meta_hidden, 1),
        )

    def forward(self, x):
        """Base models produce logits, meta-learner combines them."""
        base_outs = [m(x) for m in self.base_models]  # list of (batch, 1)
        stacked = torch.cat(base_outs, dim=1)  # (batch, n_base)
        return self.meta(stacked)  # (batch, 1)

    def eval(self):
        for m in self.base_models:
            m.eval()
        self.meta.eval()

    @torch.no_grad()
    def get_base_probs(self, x):
        """Get base model probabilities (for meta-feature extraction)."""
        self.eval()
        base_outs = [torch.sigmoid(m(x)) for m in self.base_models]
        return torch.cat(base_outs, dim=1)  # (batch, n_base)

    def save(self, path):
        state = {
            "base_models": [{k: v.cpu() for k, v in m.state_dict().items()} for m in self.base_models],
            "meta": {k: v.cpu() for k, v in self.meta.state_dict().items()},
        }
        torch.save(state, path)

    @classmethod
    def load(cls, path, base_models, device="cpu"):
        data = torch.load(path, map_location=device, weights_only=True)
        for state, m in zip(data["base_models"], base_models):
            m.load_state_dict(state)
            m.to(device)
        ensemble = cls(base_models)
        ensemble.meta.load_state_dict(data["meta"])
        ensemble.to(device)
        return ensemble


def train_stacking(stacking_ensemble, train_ds, val_ds, config, device, epochs=20, lr=0.001):
    """Train stacking ensemble: freeze base models, train meta-learner."""
    from torch.utils.data import DataLoader

    stacking_ensemble.to(device)
    stacking_ensemble.eval()

    # Freeze base models
    for p in stacking_ensemble.base_models.parameters():
        p.requires_grad = False

    optimizer = torch.optim.Adam(stacking_ensemble.meta.parameters(), lr=lr)
    criterion = nn.BCEWithLogitsLoss()

    train_loader = DataLoader(train_ds, batch_size=config.batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=config.batch_size)

    best_val_loss = float("inf")
    best_state = None
    patience = 7
    patience_counter = 0

    for epoch in range(epochs):
        # Train meta-learner
        stacking_ensemble.train()
        total_loss = 0
        correct = 0
        total = 0
        for x, y in train_loader:
            x, y = x.to(device), y.to(device).unsqueeze(1)
            optimizer.zero_grad()
            out = stacking_ensemble(x)
            loss = criterion(out, y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * x.size(0)
            correct += ((torch.sigmoid(out) > 0.5).float() == y).sum().item()
            total += x.size(0)
        train_loss = total_loss / total
        train_acc = correct / total

        # Validate
        stacking_ensemble.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for x, y in val_loader:
                x, y = x.to(device), y.to(device).unsqueeze(1)
                out = stacking_ensemble(x)
                val_loss += criterion(out, y).item() * x.size(0)
                val_correct += ((torch.sigmoid(out) > 0.5).float() == y).sum().item()
                val_total += y.size(0)
        val_loss /= val_total
        val_acc = val_correct / val_total

        print(f"  Epoch {epoch+1:2d} | train_loss={train_loss:.4f} acc={train_acc:.3f} | val_loss={val_loss:.4f} acc={val_acc:.3f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in stacking_ensemble.meta.state_dict().items()}
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break

    if best_state:
        stacking_ensemble.meta.load_state_dict(best_state)
    return stacking_ensemble
