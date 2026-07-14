import os
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
        out, _ = self.lstm(x)
        return self.head(out[:, -1, :])


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
        out = out[:, :, :x.size(2)]
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
        out = self.tcn(x.permute(0, 2, 1))
        out = out[:, :, -1]
        return self.head(out)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class AttentionBlock(nn.Module):
    def __init__(self, hidden_size: int, nhead: int = 8, dropout: float = 0.1):
        super().__init__()
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size, num_heads=nhead, dropout=dropout, batch_first=True,
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
        attn_out, _ = self.attention(x, x, x)
        x = self.norm1(x + attn_out)
        ffn_out = self.ffn(x)
        x = self.norm2(x + ffn_out)
        return x


class AttentionTransformer(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_projection = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.pos_encoding = PositionalEncoding(hidden_size, dropout)
        nhead = min(8, hidden_size // 16)
        self.attention_blocks = nn.ModuleList([
            AttentionBlock(hidden_size, nhead, dropout) for _ in range(num_layers)
        ])
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
        x = x[:, -1, :]
        return self.head(x)


class TransformerModel(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float = 0.2):
        super().__init__()
        self.input_projection = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
        )
        self.pos_encoding = PositionalEncoding(hidden_size, dropout)
        nhead = min(8, hidden_size // 16)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size, nhead=nhead, dim_feedforward=hidden_size * 4,
            dropout=dropout, batch_first=True, activation='gelu', norm_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
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
        x = self.transformer(x)
        x = x[:, -1, :]
        return self.head(x)


def build_model(config, input_size: int) -> nn.Module:
    model_type = config.model_type.lower()
    if model_type == "tcn":
        return TCNModel(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "transformer":
        return TransformerModel(input_size, config.hidden_size, config.num_layers, config.dropout)
    elif model_type == "attention":
        return AttentionTransformer(input_size, config.hidden_size, config.num_layers, config.dropout)
    return LSTMModel(input_size, config.hidden_size, config.num_layers, config.dropout)


class Ensemble:
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
        logits = torch.stack([m(x) for m in self.models])
        weights = torch.tensor(self.weights, device=x.device).view(-1, 1, 1)
        return (logits * weights).sum(dim=0)

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


class SklearnModelWrapper:
    def __init__(self, model, window: int, n_features: int):
        self.model = model
        self.window = window
        self.n_features = n_features

    def fit(self, X_flat: np.ndarray, y: np.ndarray):
        self.model.fit(X_flat, y)

    def predict_proba_logits(self, X_flat: np.ndarray) -> np.ndarray:
        proba = self.model.predict_proba(X_flat)[:, 1]
        eps = 1e-7
        proba = np.clip(proba, eps, 1 - eps)
        return np.log(proba / (1 - proba))

    def eval(self):
        pass

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if isinstance(x, torch.Tensor):
            x_np = x.detach().cpu().numpy()
        else:
            x_np = x
        batch_size = x_np.shape[0]
        X_flat = x_np.reshape(batch_size, -1)
        logits = self.predict_proba_logits(X_flat)
        return torch.tensor(logits, dtype=torch.float32).unsqueeze(1)


def _train_sklearn_model(model_cls, X_train, y_train, n_cpu=2, **kwargs):
    os.environ["OMP_NUM_THREADS"] = str(n_cpu)
    os.environ["MKL_NUM_THREADS"] = str(n_cpu)
    kwargs.pop("n_jobs", None)
    kwargs.pop("thread_count", None)
    m = model_cls(**kwargs, random_state=42, n_jobs=1)
    m.fit(X_train, y_train)
    return m


def build_sklearn_models(X_train: np.ndarray, y_train: np.ndarray,
                         window: int, n_features: int, n_cpu: int = 2) -> list:
    models = []
    try:
        from xgboost import XGBClassifier
        xgb = _train_sklearn_model(
            XGBClassifier, X_train, y_train, n_cpu,
            n_estimators=100, max_depth=5, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, eval_metric="logloss",
            verbosity=0, use_label_encoder=False,
        )
        models.append(("xgboost", SklearnModelWrapper(xgb, window, n_features)))
    except ImportError:
        pass

    try:
        from catboost import CatBoostClassifier
        os.environ["OMP_NUM_THREADS"] = str(n_cpu)
        os.environ["MKL_NUM_THREADS"] = str(n_cpu)
        cat = CatBoostClassifier(
            iterations=100, depth=6, learning_rate=0.05,
            random_seed=42, verbose=0, thread_count=n_cpu,
        )
        cat.fit(X_train, y_train)
        models.append(("catboost", SklearnModelWrapper(cat, window, n_features)))
    except ImportError:
        pass

    try:
        from lightgbm import LGBMClassifier
        lgb = _train_sklearn_model(
            LGBMClassifier, X_train, y_train, n_cpu,
            n_estimators=100, max_depth=6, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, verbose=-1,
        )
        models.append(("lightgbm", SklearnModelWrapper(lgb, window, n_features)))
    except ImportError:
        pass

    from sklearn.ensemble import RandomForestClassifier
    rf = _train_sklearn_model(
        RandomForestClassifier, X_train, y_train, n_cpu,
        n_estimators=100, max_depth=8, min_samples_leaf=5,
    )
    models.append(("random_forest", SklearnModelWrapper(rf, window, n_features)))
    return models


class HybridEnsemble:
    def __init__(self, neural_models: list, sklearn_wrappers: list = None, weights: list = None):
        self.neural_models = neural_models
        self.sklearn_wrappers = sklearn_wrappers or []
        self.all_models = neural_models + self.sklearn_wrappers
        if weights is None:
            self.weights = [1.0 / len(self.all_models)] * len(self.all_models)
        else:
            total = sum(weights)
            self.weights = [w / total for w in weights]

    def eval(self):
        for m in self.neural_models:
            if hasattr(m, "eval"):
                m.eval()

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        logits = []
        for m in self.all_models:
            logits.append(m(x))
        logits = torch.stack(logits)
        weights = torch.tensor(self.weights, device=x.device).view(-1, 1, 1)
        return (logits * weights).sum(dim=0)
