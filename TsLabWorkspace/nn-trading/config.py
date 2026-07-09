from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    # Data
    symbol: str = "BTC-USD"
    interval: str = "1d"  # Daily data for longer history
    period: str = "1820d"  # 5 years of data

    # Features
    window: int = 30  # bars lookback
    horizon: int = 5  # bars ahead for label
    threshold: float = 0.001  # price change threshold for label

    # Model - increased capacity with attention
    hidden_size: int = 64
    num_layers: int = 2
    dropout: float = 0.35
    model_type: str = "attention"  # "lstm", "tcn", "transformer", "attention"
    n_models: int = 1  # single model for now

    # Feature selection - use FEATURE_COLS
    use_feature_selection: bool = False
    max_features: int = 14

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

    # Paths
    data_dir: Path = Path("data")
    model_dir: Path = Path("models")
    result_dir: Path = Path("results")
