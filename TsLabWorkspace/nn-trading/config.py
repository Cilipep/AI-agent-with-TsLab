from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    # Data
    symbol: str = "BTCUSDT"
    interval: str = "1d"
    period: str = "1820d"

    # Features
    window: int = 30
    horizon: int = 20         # 20 bars = 5 hours on 15m (was 5 = 75 min)
    threshold: float = 0.005  # 0.5% minimum move (was 0.1%)
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
    take_profit_pct: float = 0.06   # 3:1 R/R (was 2:1)
    risk_per_trade: float = 0.02

    # Transaction costs (realistic for limit orders + VIP tier)
    commission_pct: float = 0.0002   # 0.02% maker fee (was 0.1% taker)
    slippage_pct: float = 0.0001     # 0.01% slippage (was 0.05%)
    spread_pct: float = 0.0002       # 0.02% spread for liquid pairs (was 0.05%)

    # Walk-forward
    n_folds: int = 20
    use_stacking: bool = False

    # Hybrid ensemble
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
