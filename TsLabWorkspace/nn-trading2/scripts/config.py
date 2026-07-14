from pathlib import Path
from dataclasses import dataclass


@dataclass
class Config:
    # Data
    symbol: str = "BTCUSDT"
    interval: str = "1h"
    period: str = "365d"

    # Features
    window: int = 30
    horizon: int = 5
    threshold: float = 0.001
    max_features: int = 40
    use_feature_selection: bool = True

    # Model
    hidden_size: int = 64
    num_layers: int = 2
    nhead: int = 8
    dropout: float = 0.35
    model_type: str = "attention"
    n_models: int = 3

    # Training
    batch_size: int = 64
    learning_rate: float = 1e-3
    epochs: int = 30
    patience: int = 7
    train_ratio: float = 0.7
    val_ratio: float = 0.15

    # Risk management
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    risk_per_trade: float = 0.02
    trailing_stop_pct: float = 0.015

    # Transaction costs
    commission_pct: float = 0.001
    slippage_pct: float = 0.0005
    spread_pct: float = 0.0005

    # Walk-forward
    n_folds: int = 3
    embargo: int = 7

    # Hybrid ensemble (neural + sklearn)
    use_xgboost: bool = True
    use_catboost: bool = True
    use_lightgbm: bool = True
    use_random_forest: bool = True

    # CPU throttling
    n_cpu_threads: int = 2

    # Paths
    data_dir: Path = Path("data")
    model_dir: Path = Path("models")
    result_dir: Path = Path("results")
