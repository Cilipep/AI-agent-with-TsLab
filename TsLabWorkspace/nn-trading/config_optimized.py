"""Optimized configuration for NEAR and SOL."""
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ConfigNear:
    """Optimized for NEAR/USDT."""
    symbol: str = "NEARUSDT"
    interval: str = "1d"
    period: str = "1820d"

    # Features
    window: int = 30
    horizon: int = 5
    threshold: float = 0.001
    max_features: int = 50
    use_feature_selection: bool = True

    # Model
    hidden_size: int = 32
    num_layers: int = 2
    nhead: int = 4
    dropout: float = 0.3246
    model_type: str = "attention"
    n_models: int = 3

    # Training
    batch_size: int = 32
    learning_rate: float = 0.000253
    epochs: int = 25
    patience: int = 7
    train_ratio: float = 0.7
    val_ratio: float = 0.15

    # Risk management
    stop_loss_pct: float = 0.0256
    take_profit_pct: float = 0.1111
    risk_per_trade: float = 0.02

    # Transaction costs
    commission_pct: float = 0.001
    slippage_pct: float = 0.0005
    spread_pct: float = 0.0005

    # Walk-forward
    n_folds: int = 5
    use_stacking: bool = False

    # Hybrid ensemble
    use_xgboost: bool = True
    use_catboost: bool = True
    use_lightgbm: bool = True
    use_random_forest: bool = True

    # CPU
    n_cpu_threads: int = 2

    # Paths
    data_dir: Path = Path("data")
    model_dir: Path = Path("models")
    result_dir: Path = Path("results")


@dataclass
class ConfigSol:
    """Optimized for SOL/USDT."""
    symbol: str = "SOLUSDT"
    interval: str = "1d"
    period: str = "1820d"

    # Features
    window: int = 40
    horizon: int = 5
    threshold: float = 0.001
    max_features: int = 30
    use_feature_selection: bool = True

    # Model
    hidden_size: int = 32
    num_layers: int = 1
    nhead: int = 8
    dropout: float = 0.4989
    model_type: str = "attention"
    n_models: int = 3

    # Training
    batch_size: int = 64
    learning_rate: float = 0.000174
    epochs: int = 25
    patience: int = 7
    train_ratio: float = 0.7
    val_ratio: float = 0.15

    # Risk management
    stop_loss_pct: float = 0.0224
    take_profit_pct: float = 0.0702
    risk_per_trade: float = 0.02

    # Transaction costs
    commission_pct: float = 0.001
    slippage_pct: float = 0.0005
    spread_pct: float = 0.0005

    # Walk-forward
    n_folds: int = 5
    use_stacking: bool = False

    # Hybrid ensemble
    use_xgboost: bool = True
    use_catboost: bool = True
    use_lightgbm: bool = True
    use_random_forest: bool = True

    # CPU
    n_cpu_threads: int = 2

    # Paths
    data_dir: Path = Path("data")
    model_dir: Path = Path("models")
    result_dir: Path = Path("results")
