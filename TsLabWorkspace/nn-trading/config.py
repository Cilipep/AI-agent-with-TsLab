from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    # Data
    symbol: str = "BTCUSDT"
    interval: str = "1d"  # Daily data for longer history
    period: str = "1820d"  # 5 years of data

    # Features
    window: int = 30  # bars lookback
    horizon: int = 5  # bars ahead for label
    threshold: float = 0.001  # price change threshold for label
    max_features: int = 40  # auto-select top N features
    use_feature_selection: bool = True

    # Model
    hidden_size: int = 64
    num_layers: int = 2
    nhead: int = 8  # attention heads
    dropout: float = 0.35
    model_type: str = "attention"  # "lstm", "tcn", "transformer", "attention"
    n_models: int = 3  # base models in ensemble

    # Training
    batch_size: int = 64
    learning_rate: float = 1e-3
    epochs: int = 30
    patience: int = 7  # early stopping
    train_ratio: float = 0.7
    val_ratio: float = 0.15

    # Risk management
    stop_loss_pct: float = 0.02       # 2% stop-loss
    take_profit_pct: float = 0.04     # 4% take-profit (2:1 R/R)
    risk_per_trade: float = 0.02      # 2% of equity per trade

    # Transaction costs
    commission_pct: float = 0.001     # 0.1% taker fee
    slippage_pct: float = 0.0005      # 0.05% slippage
    spread_pct: float = 0.0005        # 0.05% spread (liquid pairs)

    # Walk-forward
    n_folds: int = 20                 # Anchored walk-forward folds
    use_stacking: bool = False        # Use StackingEnsemble

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
